AUTH={"Authorization":"Bearer good-token"}
def test_product_reviews_are_public(client):
    response=client.get('/api/v1/products/FP0001/reviews')
    assert response.status_code==200
    assert response.json()['data']['items'][0]['rating']==5

def test_review_submission_requires_completed_owned_item_contract(client):
    response=client.post('/api/v1/reviews',json={'order_item_id':51,'rating':5,'review_text':'配料清晰'},headers=AUTH)
    assert response.status_code==201
    assert response.json()['data']['order_item_id']==51

def test_my_reviews_and_insights_require_jwt(client):
    assert client.get('/api/v1/reviews/me').status_code==401
    assert client.get('/api/v1/reviews/me',headers=AUTH).status_code==200
    rec=client.get('/api/v1/recommendations',headers=AUTH)
    assert rec.status_code==200 and rec.json()['data'][0]['reasons']
    assert client.get('/api/v1/notifications',headers=AUTH).status_code==200