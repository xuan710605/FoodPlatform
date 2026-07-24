import json
import uuid
from decimal import Decimal
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

PRICE_JOIN = """
JOIN product_price pp ON pp.spec_id=s.id AND pp.price_type='SALE' AND pp.status='ACTIVE'
 AND pp.valid_from<=CURRENT_TIMESTAMP(3) AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3))
 AND pp.valid_from=(SELECT MAX(p2.valid_from) FROM product_price p2 WHERE p2.spec_id=s.id AND p2.price_type='SALE' AND p2.status='ACTIVE' AND p2.valid_from<=CURRENT_TIMESTAMP(3) AND (p2.valid_to IS NULL OR p2.valid_to>CURRENT_TIMESTAMP(3)))
"""

ORDER_STATUS_TO_API = {
    "PENDING_SHIPMENT": "PAID",
    "SHIPPED": "SHIPPING",
}
API_STATUS_TO_DB = {"PAID":"PENDING_SHIPMENT","SHIPPING":"SHIPPED"}
ALLOWED_ACTIONS = {"PENDING_PAYMENT":["PAY","CANCEL"],"SHIPPED":["CONFIRM_RECEIPT"]}

class CommerceRepository:
    def __init__(self, session_factory: sessionmaker[Session]): self._factory=session_factory

    def get_cart(self,user_id:int)->dict[str,Any]:
        with self._factory() as session: return self._cart(session,user_id)

    def _cart(self,session:Session,user_id:int)->dict[str,Any]:
        cart=session.execute(text("SELECT id,cart_code FROM cart WHERE user_id=:u AND status='ACTIVE'"),{"u":user_id}).mappings().first()
        if not cart: return {"cart_code":"","items":[],"item_count":0,"total_quantity":0,"total_amount":Decimal("0")}
        rows=session.execute(text(f"""SELECT ci.id,p.product_code,p.product_name,s.spec_code,s.spec_name,ci.quantity,ci.selected_flag,pp.amount unit_price,pi.available_qty,
          (SELECT image_url FROM product_image WHERE product_id=p.id AND image_type='MAIN' AND status='ACTIVE' ORDER BY sort_order,id LIMIT 1) image_url,
          p.sale_status,p.review_status
          FROM cart_item ci JOIN product p ON p.id=ci.product_id JOIN product_spec s ON s.id=ci.spec_id {PRICE_JOIN}
          LEFT JOIN product_inventory pi ON pi.spec_id=s.id AND pi.warehouse_code='DEFAULT' WHERE ci.cart_id=:c ORDER BY ci.id"""),{"c":cart["id"]}).mappings().all()
        items=[]
        for r in rows:
            d=dict(r); d["selected"]=bool(d.pop("selected_flag")); d["stock_quantity"]=int(d.pop("available_qty") or 0); d["sellable"]=d.pop("sale_status")=="ON_SALE" and d.pop("review_status")=="APPROVED" and d["stock_quantity"]>=d["quantity"]; d["subtotal"]=d["unit_price"]*d["quantity"]; items.append(d)
        return {"cart_code":cart["cart_code"],"items":items,"item_count":len(items),"total_quantity":sum(x["quantity"] for x in items),"total_amount":sum((x["subtotal"] for x in items),Decimal("0"))}

    def add_cart_item(self,user_id:int,product_code:str,spec_code:str|None,quantity:int)->dict[str,Any]:
        with self._factory.begin() as session:
            row=session.execute(text(f"""SELECT p.id product_id,s.id spec_id,pp.amount,COALESCE(pi.available_qty,0) stock_qty FROM product p JOIN product_spec s ON s.product_id=p.id AND s.status='ACTIVE' {PRICE_JOIN} LEFT JOIN product_inventory pi ON pi.spec_id=s.id AND pi.warehouse_code='DEFAULT' WHERE p.product_code=:p AND p.is_deleted=0 AND p.sale_status='ON_SALE' AND p.review_status='APPROVED' AND (:s IS NULL AND s.is_default=1 OR s.spec_code=:s) ORDER BY s.is_default DESC,s.id LIMIT 1"""),{"p":product_code,"s":spec_code}).mappings().first()
            if not row: return {"error":"PRODUCT_NOT_SELLABLE"}
            cart_id=session.execute(text("SELECT id FROM cart WHERE user_id=:u AND status='ACTIVE'"),{"u":user_id}).scalar_one_or_none()
            if cart_id is None:
                cart_id=session.execute(text("INSERT INTO cart(cart_code,user_id,status) VALUES(:c,:u,'ACTIVE')"),{"c":"CART"+uuid.uuid4().hex[:20].upper(),"u":user_id}).lastrowid
            current=session.execute(text("SELECT id,quantity FROM cart_item WHERE cart_id=:c AND spec_id=:s"),{"c":cart_id,"s":row["spec_id"]}).mappings().first()
            desired=quantity+(current["quantity"] if current else 0)
            if desired>row["stock_qty"]: return {"error":"INSUFFICIENT_STOCK","available":row["stock_qty"]}
            if current: session.execute(text("UPDATE cart_item SET quantity=:q,selected_flag=1 WHERE id=:id"),{"q":desired,"id":current["id"]}); item_id=current["id"]
            else: item_id=session.execute(text("INSERT INTO cart_item(cart_id,product_id,spec_id,quantity,selected_flag,added_price) VALUES(:c,:p,:s,:q,1,:a)"),{"c":cart_id,"p":row["product_id"],"s":row["spec_id"],"q":quantity,"a":row["amount"]}).lastrowid
        return next(x for x in self.get_cart(user_id)["items"] if x["id"]==item_id)

    def update_cart_item(self,user_id:int,item_id:int,quantity:int)->dict[str,Any]|None:
        with self._factory.begin() as session:
            row=session.execute(text("SELECT ci.id,COALESCE(pi.available_qty,0) stock_qty FROM cart_item ci JOIN cart c ON c.id=ci.cart_id LEFT JOIN product_inventory pi ON pi.spec_id=ci.spec_id AND pi.warehouse_code='DEFAULT' WHERE ci.id=:id AND c.user_id=:u AND c.status='ACTIVE'"),{"id":item_id,"u":user_id}).mappings().first()
            if not row:return None
            if quantity>row["stock_qty"]:return {"error":"INSUFFICIENT_STOCK","available":row["stock_qty"]}
            session.execute(text("UPDATE cart_item SET quantity=:q WHERE id=:id"),{"q":quantity,"id":item_id})
        return next(x for x in self.get_cart(user_id)["items"] if x["id"]==item_id)

    def delete_cart_item(self,user_id:int,item_id:int)->bool:
        with self._factory.begin() as session:
            result=session.execute(text("DELETE ci FROM cart_item ci JOIN cart c ON c.id=ci.cart_id WHERE ci.id=:id AND c.user_id=:u AND c.status='ACTIVE'"),{"id":item_id,"u":user_id})
            return result.rowcount>0

    def create_order(self,user_id:int,item_ids:list[int]|None,receiver:dict[str,str],remark:str|None)->dict[str,Any]:
        with self._factory.begin() as session:
            params={"u":user_id}; id_clause=""
            if item_ids:
                keys=[]
                for n,value in enumerate(item_ids): params[f"i{n}"]=value; keys.append(f":i{n}")
                id_clause=" AND ci.id IN ("+",".join(keys)+")"
            rows=session.execute(text(f"""SELECT ci.id cart_item_id,ci.quantity,p.id product_id,p.product_code,p.product_name,p.merchant_id,s.id spec_id,s.spec_code,s.spec_name,pp.amount,
              pi.id inventory_id,pi.available_qty,COALESCE((SELECT MAX(version_no) FROM product_ingredient_snapshot pis WHERE pis.product_id=p.id AND pis.effective_to IS NULL),NULL) ingredient_version,
              (SELECT image_url FROM product_image WHERE product_id=p.id AND image_type='MAIN' AND status='ACTIVE' ORDER BY sort_order,id LIMIT 1) image_url
              FROM cart_item ci JOIN cart c ON c.id=ci.cart_id JOIN product p ON p.id=ci.product_id AND p.sale_status='ON_SALE' AND p.review_status='APPROVED' AND p.is_deleted=0 JOIN product_spec s ON s.id=ci.spec_id AND s.status='ACTIVE' {PRICE_JOIN} JOIN product_inventory pi ON pi.spec_id=s.id AND pi.warehouse_code='DEFAULT'
              WHERE c.user_id=:u AND c.status='ACTIVE' AND ci.selected_flag=1{id_clause} ORDER BY pi.id FOR UPDATE"""),params).mappings().all()
            if not rows:return {"error":"CART_EMPTY"}
            if len({r["merchant_id"] for r in rows})!=1:return {"error":"MULTIPLE_MERCHANTS"}
            for r in rows:
                if r["quantity"]>r["available_qty"]:return {"error":"INSUFFICIENT_STOCK","product_code":r["product_code"],"available":r["available_qty"]}
            order_no="ORD"+uuid.uuid4().hex[:20].upper(); goods=sum((r["amount"]*r["quantity"] for r in rows),Decimal("0")); shipping=Decimal("0") if goods>=59 else Decimal("6")
            order_id=session.execute(text("""INSERT INTO order_info(order_no,user_id,merchant_id,order_status,payment_status,receiver_snapshot,goods_amount,discount_amount,shipping_amount,payable_amount,paid_amount,buyer_remark,placed_at) VALUES(:no,:u,:m,'PENDING_PAYMENT','UNPAID',CAST(:receiver AS JSON),:goods,0,:shipping,:payable,0,:remark,CURRENT_TIMESTAMP(3))"""),{"no":order_no,"u":user_id,"m":rows[0]["merchant_id"],"receiver":json.dumps(receiver,ensure_ascii=False),"goods":goods,"shipping":shipping,"payable":goods+shipping,"remark":remark}).lastrowid
            for n,r in enumerate(rows,1):
                session.execute(text("""INSERT INTO order_item(order_id,order_item_code,product_id,spec_id,product_code_snapshot,product_name_snapshot,spec_code_snapshot,spec_name_snapshot,image_url_snapshot,unit_price,quantity,subtotal_amount,ingredient_version_snapshot) VALUES(:o,:code,:p,:s,:pc,:pn,:sc,:sn,:img,:price,:q,:sub,:version)"""),{"o":order_id,"code":f"{order_no}-{n:03d}","p":r["product_id"],"s":r["spec_id"],"pc":r["product_code"],"pn":r["product_name"],"sc":r["spec_code"],"sn":r["spec_name"],"img":r["image_url"],"price":r["amount"],"q":r["quantity"],"sub":r["amount"]*r["quantity"],"version":r["ingredient_version"]})
                before=r["available_qty"]; after=before-r["quantity"]
                session.execute(text("UPDATE product_inventory SET available_qty=:after,inventory_status=CASE WHEN :after=0 THEN 'OUT_OF_STOCK' WHEN :after<=warning_threshold THEN 'LOW' ELSE 'NORMAL' END,version_no=version_no+1 WHERE id=:id"),{"after":after,"id":r["inventory_id"]})
                session.execute(text("INSERT INTO inventory_change_log(inventory_id,business_type,business_code,quantity_delta,before_qty,after_qty,operator_user_id,reason) VALUES(:id,'ORDER_DEDUCT',:code,:delta,:before,:after,:u,'order created')"),{"id":r["inventory_id"],"code":order_no,"delta":-r["quantity"],"before":before,"after":after,"u":user_id})
            session.execute(text("DELETE FROM cart_item WHERE id IN ("+",".join(str(int(r["cart_item_id"])) for r in rows)+")"))
        return self.get_order(user_id,order_id)

    def list_orders(self,user_id:int,page:int,page_size:int,status:str|None=None)->dict[str,Any]:
        with self._factory() as session:
            params={"u":user_id};status_clause=""
            if status:params["status"]=API_STATUS_TO_DB.get(status,status);status_clause=" AND order_status=:status"
            total=session.execute(text("SELECT COUNT(*) FROM order_info WHERE user_id=:u"+status_clause),params).scalar_one()
            ids=session.execute(text("SELECT id FROM order_info WHERE user_id=:u"+status_clause+" ORDER BY placed_at DESC LIMIT :limit OFFSET :offset"),{**params,"limit":page_size,"offset":(page-1)*page_size}).scalars().all()
        return {"total":total,"page":page,"page_size":page_size,"items":[self.get_order(user_id,x) for x in ids]}

    def get_order(self,user_id:int,order_id:int)->dict[str,Any]|None:
        with self._factory() as session:
            order=session.execute(text("SELECT id,order_no,order_status status,payment_status,receiver_snapshot,goods_amount,shipping_amount,payable_amount,paid_amount,buyer_remark,placed_at,paid_at,shipped_at,completed_at,cancelled_at,cancel_reason FROM order_info WHERE id=:id AND user_id=:u"),{"id":order_id,"u":user_id}).mappings().first()
            if not order:return None
            items=session.execute(text("""SELECT oi.id,oi.product_code_snapshot product_code,oi.product_name_snapshot product_name,oi.spec_code_snapshot spec_code,oi.spec_name_snapshot spec_name,oi.image_url_snapshot image_url,oi.unit_price,oi.quantity,oi.subtotal_amount subtotal,oi.ingredient_version_snapshot ingredient_version,EXISTS(SELECT 1 FROM product_review pr WHERE pr.order_item_id=oi.id) reviewed FROM order_item oi WHERE oi.order_id=:id ORDER BY oi.id"""),{"id":order_id}).mappings().all()
            result=dict(order); db_status=result["status"]; result["status"]=ORDER_STATUS_TO_API.get(db_status,db_status); result["allowed_actions"]=ALLOWED_ACTIONS.get(db_status,[]); snapshot=result.get("receiver_snapshot"); result["receiver_snapshot"]=json.loads(snapshot) if isinstance(snapshot,str) else snapshot; result["items"]=[dict(x)|{"reviewed":bool(x["reviewed"]),"can_review":db_status=="COMPLETED" and not bool(x["reviewed"])} for x in items]; reviewed=sum(1 for x in result["items"] if x["reviewed"]); total=len(result["items"]); result["review_status"]="UNAVAILABLE" if db_status!="COMPLETED" else "COMPLETED" if reviewed==total else "PARTIAL" if reviewed else "PENDING"; return result

    def pay_order(self,user_id:int,order_id:int,channel:str)->dict[str,Any]|None:
        with self._factory.begin() as session:
            row=session.execute(text("SELECT id,order_no,order_status,payable_amount FROM order_info WHERE id=:id AND user_id=:u FOR UPDATE"),{"id":order_id,"u":user_id}).mappings().first()
            if not row:return None
            if row["order_status"]!="PENDING_PAYMENT":return {"error":"INVALID_ORDER_STATUS"}
            payment_no="PAY"+uuid.uuid4().hex[:20].upper()
            session.execute(text("INSERT INTO payment_record(payment_no,order_id,payment_channel,payment_status,amount,provider_transaction_no,requested_at,completed_at) VALUES(:no,:o,:ch,'SUCCESS',:a,:tx,CURRENT_TIMESTAMP(3),CURRENT_TIMESTAMP(3))"),{"no":payment_no,"o":order_id,"ch":channel,"a":row["payable_amount"],"tx":"MOCK"+uuid.uuid4().hex[:20].upper()})
            session.execute(text("UPDATE order_info SET order_status='PENDING_SHIPMENT',payment_status='PAID',paid_amount=payable_amount,paid_at=CURRENT_TIMESTAMP(3) WHERE id=:id"),{"id":order_id})
        return self.get_order(user_id,order_id)

    def cancel_order(self,user_id:int,order_id:int)->dict[str,Any]|None:
        with self._factory.begin() as session:
            order=session.execute(text("SELECT id,order_no,order_status FROM order_info WHERE id=:id AND user_id=:u FOR UPDATE"),{"id":order_id,"u":user_id}).mappings().first()
            if not order:return None
            if order["order_status"]!="PENDING_PAYMENT":return {"error":"INVALID_ORDER_STATUS"}
            rows=session.execute(text("SELECT oi.quantity,pi.id inventory_id,pi.available_qty FROM order_item oi JOIN product_inventory pi ON pi.spec_id=oi.spec_id AND pi.warehouse_code='DEFAULT' WHERE oi.order_id=:o ORDER BY pi.id FOR UPDATE"),{"o":order_id}).mappings().all()
            exists=session.execute(text("SELECT 1 FROM inventory_change_log WHERE business_type='ORDER_RELEASE' AND business_code=:code LIMIT 1"),{"code":order["order_no"]}).first()
            if exists:return {"error":"ALREADY_RESTORED"}
            for r in rows:
                after=r["available_qty"]+r["quantity"]
                session.execute(text("UPDATE product_inventory SET available_qty=:after,inventory_status=CASE WHEN :after<=warning_threshold THEN 'LOW' ELSE 'NORMAL' END,version_no=version_no+1 WHERE id=:id"),{"after":after,"id":r["inventory_id"]})
                session.execute(text("INSERT INTO inventory_change_log(inventory_id,business_type,business_code,quantity_delta,before_qty,after_qty,operator_user_id,reason) VALUES(:id,'ORDER_RELEASE',:code,:q,:before,:after,:u,'order cancelled')"),{"id":r["inventory_id"],"code":order["order_no"],"q":r["quantity"],"before":r["available_qty"],"after":after,"u":user_id})
            session.execute(text("UPDATE order_info SET order_status='CANCELLED',cancelled_at=CURRENT_TIMESTAMP(3),cancel_reason='Cancelled by consumer' WHERE id=:id"),{"id":order_id})
        return self.get_order(user_id,order_id)

    def confirm_receipt(self,user_id:int,order_id:int)->dict[str,Any]|None:
        with self._factory.begin() as session:
            row=session.execute(text("SELECT id,order_status FROM order_info WHERE id=:id AND user_id=:u FOR UPDATE"),{"id":order_id,"u":user_id}).mappings().first()
            if not row:return None
            if row["order_status"]!="SHIPPED":return {"error":"INVALID_ORDER_STATUS"}
            session.execute(text("UPDATE order_info SET order_status='COMPLETED',completed_at=CURRENT_TIMESTAMP(3) WHERE id=:id"),{"id":order_id})
        return self.get_order(user_id,order_id)