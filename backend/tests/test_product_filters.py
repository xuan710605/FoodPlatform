from app.main import app

def test_product_query_forwards_all_database_filters(client):
    response=client.get('/api/v1/products',params=[
        ('keyword','milk'),('category','乳品酸奶'),('brand','每日牧场'),
        ('exclude','牛奶'),('exclude','花生'),('sugar_max','5'),
        ('fat_max','10'),('protein_min','8'),('sodium_max','500'),
        ('price_min','10'),('price_max','60')])
    assert response.status_code==200
    query=app.state.product_service.last_filters
    assert query['category']=='乳品酸奶'
    assert query['brand']=='每日牧场'
    assert query['excluded_ingredients']==['牛奶','花生']
    assert str(query['sugar_max'])=='5'
    assert str(query['protein_min'])=='8'
    assert str(query['price_min'])=='10'
    assert str(query['price_max'])=='60'

def test_product_category_counts_are_from_service(client):
    response=client.get('/api/v1/products/categories')
    assert response.status_code==200
    assert response.json()['data']==[{
        'category_code':'CAT001','category_name':'早餐麦片','product_count':1}]

def test_negative_nutrition_filter_is_rejected(client):
    response=client.get('/api/v1/products?sugar_max=-1')
    assert response.status_code==422
