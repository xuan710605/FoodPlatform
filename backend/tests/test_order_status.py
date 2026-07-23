from app.repositories.commerce_repository import ORDER_STATUS_TO_API


def test_order_status_mapping_preserves_database_contract():
    assert ORDER_STATUS_TO_API["PENDING_SHIPMENT"] == "PAID"
    assert ORDER_STATUS_TO_API["SHIPPED"] == "SHIPPING"
