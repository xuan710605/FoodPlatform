AUTH={"Authorization":"Bearer good-token"}
def test_add_cart_item(client):
 r=client.post("/api/v1/cart/items",json={"product_code":"FP0001","quantity":2},headers=AUTH);assert r.status_code==201;assert r.json()["data"]["subtotal"]=="65.80"
def test_update_cart_quantity(client):
 r=client.put("/api/v1/cart/items/7",json={"quantity":3},headers=AUTH);assert r.status_code==200;assert r.json()["data"]["quantity"]==3
def test_delete_cart_item(client):
 assert client.delete("/api/v1/cart/items/7",headers=AUTH).status_code==200
def test_cart_rejects_insufficient_stock(client):
 r=client.post("/api/v1/cart/items",json={"product_code":"FP0001","quantity":99},headers=AUTH);assert r.status_code==409;assert r.json()["error"]["code"]=="INSUFFICIENT_STOCK"
def test_create_order_contains_snapshot(client):
 r=client.post("/api/v1/orders",json={"receiver":{"name":"测试用户","phone":"13800000000","address":"测试地址一号"}},headers=AUTH);assert r.status_code==201;assert r.json()["data"]["items"][0]["product_code"]=="FP0001"
def test_order_payment_success(client):
 r=client.post("/api/v1/orders/31/pay",json={"channel":"MOCK_BALANCE"},headers=AUTH);assert r.status_code==200;assert r.json()["data"]["status"]=="PAID";assert r.json()["data"]["paid_at"] is not None
def test_cancel_order(client):
 r=client.post("/api/v1/orders/31/cancel",headers=AUTH);assert r.status_code==200;assert r.json()["data"]["status"]=="CANCELLED"
def test_cart_requires_login(client):
 assert client.get("/api/v1/cart").status_code==401

class InventoryRepositoryStub:
 def __init__(self): self.stock=10;self.status="PENDING_PAYMENT"
 def create_order(self,*_args): self.stock-=2;return {"id":31,"status":"PENDING_PAYMENT"}
 def cancel_order(self,*_args): self.stock+=2;self.status="CANCELLED";return {"id":31,"status":"CANCELLED"}

def test_create_deducts_and_cancel_restores_inventory():
 from app.services.order_service import OrderService
 repo=InventoryRepositoryStub();service=OrderService(repo)
 service.create(21,{"cart_item_ids":[7],"receiver":{"name":"测试","phone":"13800000000","address":"测试地址 1 号"},"buyer_remark":None})
 assert repo.stock==8
 service.cancel(21,31)
 assert repo.stock==10