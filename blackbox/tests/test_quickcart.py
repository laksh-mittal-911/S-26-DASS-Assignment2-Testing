import pytest
import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8080/api/v1"
ADMIN_HEADERS = {"X-Roll-Number": "2024113003"}
HEADERS = {"X-Roll-Number": "2024113003", "X-User-ID": "1"}

def get_admin_data(endpoint):
    return requests.get(f"{BASE_URL}/admin/{endpoint}", headers=ADMIN_HEADERS).json()

def extract_id(res_json, default_key='address_id'):
    if default_key in res_json: return res_json[default_key]
    if 'id' in res_json: return res_json['id']
    for k, v in res_json.items():
        if isinstance(v, dict) and default_key in v: return v[default_key]
        if isinstance(v, dict) and 'id' in v: return v['id']
    return None

# --- 1. Global Headers & Auth ---
def test_missing_roll_number():
    res = requests.get(f"{BASE_URL}/profile", headers={"X-User-ID": "1"})
    assert res.status_code == 401
    
def test_invalid_roll_number():
    res = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "abc", "X-User-ID": "1"})
    assert res.status_code == 400

def test_missing_user_id():
    res = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "2024113003"})
    assert res.status_code == 400

def test_invalid_user_id():
    res = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "2024113003", "X-User-ID": "abc"})
    assert res.status_code == 400

def test_admin_no_user_id_required():
    res = requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": "2024113003"})
    assert res.status_code == 200

# --- 2. Admin APIs ---
@pytest.mark.parametrize("endpoint", [
    "users", "users/1", "carts", "orders", "products", "coupons", "tickets", "addresses"
])
def test_admin_endpoints_accessible(endpoint):
    res = requests.get(f"{BASE_URL}/admin/{endpoint}", headers=ADMIN_HEADERS)
    assert res.status_code in [200, 404]

# --- 3. Profile ---
def test_get_profile():
    res = requests.get(f"{BASE_URL}/profile", headers=HEADERS)
    assert res.status_code == 200

def test_put_profile_valid():
    res = requests.put(f"{BASE_URL}/profile", json={"name": "Valid Name", "phone": "1234567890"}, headers=HEADERS)
    assert res.status_code == 200

def test_put_profile_name_too_short():
    res = requests.put(f"{BASE_URL}/profile", json={"name": "A", "phone": "1234567890"}, headers=HEADERS)
    assert res.status_code == 400

def test_put_profile_name_too_long():
    res = requests.put(f"{BASE_URL}/profile", json={"name": "A"*51, "phone": "1234567890"}, headers=HEADERS)
    assert res.status_code == 400

def test_put_profile_phone_not_10_digits():
    res = requests.put(f"{BASE_URL}/profile", json={"name": "Valid", "phone": "123456789"}, headers=HEADERS)
    assert res.status_code == 400
    res = requests.put(f"{BASE_URL}/profile", json={"name": "Valid", "phone": "12345678901"}, headers=HEADERS)
    assert res.status_code == 400

def test_put_profile_phone_invalid_chars():
    res = requests.put(f"{BASE_URL}/profile", json={"name": "Valid", "phone": "abcdefghij"}, headers=HEADERS)
    assert res.status_code == 400

# --- 4. Addresses ---
def test_get_addresses():
    res = requests.get(f"{BASE_URL}/addresses", headers=HEADERS)
    assert res.status_code == 200

def test_post_address_valid():
    payload = {"label": "HOME", "street": "Main Street 1", "city": "Metropolis", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", json=payload, headers=HEADERS)
    assert res.status_code in [200, 201]

def test_post_address_invalid_label():
    payload = {"label": "WORK", "street": "Main Street 1", "city": "Metropolis", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", json=payload, headers=HEADERS)
    assert res.status_code == 400

def test_post_address_invalid_street():
    payload = {"label": "HOME", "street": "abc", "city": "Metropolis", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", json=payload, headers=HEADERS)
    assert res.status_code == 400
    
def test_post_address_invalid_city():
    payload = {"label": "HOME", "street": "Main Street", "city": "a", "pincode": "123456"}
    res = requests.post(f"{BASE_URL}/addresses", json=payload, headers=HEADERS)
    assert res.status_code == 400

def test_post_address_invalid_pincode():
    payload = {"label": "HOME", "street": "Main Street", "city": "Metropolis", "pincode": "12345"}
    res = requests.post(f"{BASE_URL}/addresses", json=payload, headers=HEADERS)
    assert res.status_code == 400

def test_address_default_logic():
    res1 = requests.post(f"{BASE_URL}/addresses", json={"label": "HOME", "street": "Street 1111", "city": "City", "pincode": "111111"}, headers=HEADERS)
    res2 = requests.post(f"{BASE_URL}/addresses", json={"label": "OFFICE", "street": "Street 2222", "city": "City", "pincode": "222222"}, headers=HEADERS)
    id1 = extract_id(res1.json())
    id2 = extract_id(res2.json())
    
    if id1 and id2:
        requests.put(f"{BASE_URL}/addresses/{id1}", json={"is_default": True}, headers=HEADERS)
        requests.put(f"{BASE_URL}/addresses/{id2}", json={"is_default": True}, headers=HEADERS)
        
        adds = requests.get(f"{BASE_URL}/addresses", headers=HEADERS).json()
        default_count = sum(1 for a in adds if a.get('is_default'))
        assert default_count == 1, "More than one default address found!"

def test_put_address_immutability():
    res = requests.post(f"{BASE_URL}/addresses", json={"label": "HOME", "street": "Immutable St", "city": "OldCity", "pincode": "123456"}, headers=HEADERS)
    addr_id = extract_id(res.json())
    
    if addr_id:
        update_res = requests.put(f"{BASE_URL}/addresses/{addr_id}", json={"label": "OFFICE", "city": "NewCity", "pincode": "654321", "street": "New St Updated", "is_default": True}, headers=HEADERS)
        updated_data = update_res.json()
        if "address" in updated_data:
            updated_data = updated_data["address"]
            
        assert updated_data.get('label') == "HOME", "Label should not be changed via update"
        assert updated_data.get('city') == "OldCity", "City should not be changed via update"
        assert updated_data.get('pincode') == "123456", "Pincode should not be changed via update"
        assert updated_data.get('street') == "New St Updated", "Street should be updated"

def test_delete_address():
    res = requests.post(f"{BASE_URL}/addresses", json={"label": "OTHER", "street": "Delete St 123", "city": "City", "pincode": "123456"}, headers=HEADERS)
    addr_id = extract_id(res.json())
    if addr_id:
        del_res = requests.delete(f"{BASE_URL}/addresses/{addr_id}", headers=HEADERS)
        assert del_res.status_code in [200, 204]
        get_res = requests.get(f"{BASE_URL}/addresses", headers=HEADERS)
        assert not any(a.get('address_id') == addr_id for a in get_res.json())

def test_delete_address_not_found():
    res = requests.delete(f"{BASE_URL}/addresses/999999", headers=HEADERS)
    assert res.status_code == 404

# --- 5. Products ---
def test_get_products():
    res = requests.get(f"{BASE_URL}/products", headers=HEADERS)
    assert res.status_code == 200
    products = res.json()
    assert all(p.get('is_active', True) for p in products), "Inactive product in list"

def test_get_product_by_id():
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        res = requests.get(f"{BASE_URL}/products/{products[0]['product_id']}", headers=HEADERS)
        assert res.status_code == 200

def test_get_product_not_found():
    res = requests.get(f"{BASE_URL}/products/999999", headers=HEADERS)
    assert res.status_code == 404

def test_get_products_filter_sort():
    res = requests.get(f"{BASE_URL}/products?sort=price_asc", headers=HEADERS)
    p = res.json()
    if len(p) >= 2:
        assert p[0]['price'] <= p[1]['price']

# --- 6. Cart ---
def test_cart_clear():
    res = requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    assert res.status_code in [200, 204]

def test_cart_add_valid():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        res = requests.post(f"{BASE_URL}/cart/add", json={"product_id": products[0]['product_id'], "quantity": 1}, headers=HEADERS)
        assert res.status_code in [200, 201]

def test_cart_add_invalid_quantity():
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        res = requests.post(f"{BASE_URL}/cart/add", json={"product_id": p_id, "quantity": 0}, headers=HEADERS)
        assert res.status_code == 400
        res = requests.post(f"{BASE_URL}/cart/add", json={"product_id": p_id, "quantity": -1}, headers=HEADERS)
        assert res.status_code == 400

def test_cart_add_not_found():
    res = requests.post(f"{BASE_URL}/cart/add", json={"product_id": 999999, "quantity": 1}, headers=HEADERS)
    assert res.status_code == 404

def test_cart_add_exceed_stock():
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p = products[0]
        res = requests.post(f"{BASE_URL}/cart/add", json={"product_id": p['product_id'], "quantity": p['stock_quantity'] + 1}, headers=HEADERS)
        assert res.status_code == 400

def test_cart_add_accumulation():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": p_id, "quantity": 1}, headers=HEADERS)
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": p_id, "quantity": 2}, headers=HEADERS)
        cart = requests.get(f"{BASE_URL}/cart", headers=HEADERS).json()
        item = next((i for i in cart.get('items', []) if i['product_id'] == p_id), None)
        assert item['quantity'] == 3, "Quantities were not added together"

def test_cart_update_quantity():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": p_id, "quantity": 1}, headers=HEADERS)
        res = requests.post(f"{BASE_URL}/cart/update", json={"product_id": p_id, "quantity": 5}, headers=HEADERS)
        assert res.status_code == 200
        cart = requests.get(f"{BASE_URL}/cart", headers=HEADERS).json()
        item = next((i for i in cart.get('items', []) if i['product_id'] == p_id), None)
        assert item['quantity'] == 5

def test_cart_update_invalid_quantity():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": p_id, "quantity": 1}, headers=HEADERS)
        res = requests.post(f"{BASE_URL}/cart/update", json={"product_id": p_id, "quantity": 0}, headers=HEADERS)
        assert res.status_code == 400

def test_cart_remove():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": p_id, "quantity": 1}, headers=HEADERS)
        res = requests.post(f"{BASE_URL}/cart/remove", json={"product_id": p_id}, headers=HEADERS)
        assert res.status_code == 200
        cart = requests.get(f"{BASE_URL}/cart", headers=HEADERS).json()
        assert len(cart.get('items', [])) == 0

def test_cart_remove_not_found():
    res = requests.post(f"{BASE_URL}/cart/remove", json={"product_id": 999999}, headers=HEADERS)
    assert res.status_code == 404

def test_cart_subtotal_and_total_hint():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if len(products) >= 2:
        p1 = products[0]
        p2 = products[1]
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": p1['product_id'], "quantity": 2}, headers=HEADERS)
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": p2['product_id'], "quantity": 3}, headers=HEADERS)
        cart = requests.get(f"{BASE_URL}/cart", headers=HEADERS).json()
        
        items = cart.get('items', [])
        expected_total = sum(i['quantity'] * i['unit_price'] for i in items)            
        assert cart['total'] == expected_total, f"Cart total sum misses last item. Expected {expected_total}, got {cart.get('total')}"

# --- 7. Coupons ---
def test_coupon_apply_and_cap_hint():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    p1 = products[0]
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": p1['product_id'], "quantity": 100}, headers=HEADERS)
    
    coupons = get_admin_data("coupons")
    capped_coupon = next((c for c in coupons if c.get('discount_type') == 'PERCENT' and c.get('max_discount', 0) > 0), None)
    
    if capped_coupon:
        res = requests.post(f"{BASE_URL}/coupon/apply", json={"code": capped_coupon['coupon_code']}, headers=HEADERS)
        assert res.status_code == 200
        cart = requests.get(f"{BASE_URL}/cart", headers=HEADERS).json()
        discount = cart.get('discount', 0)
        assert discount <= capped_coupon['max_discount'], f"Discount {discount} exceeded max_discount {capped_coupon['max_discount']}"

def test_coupon_expired():
    coupons = get_admin_data("coupons")
    expired = next((c for c in coupons if c.get('expiry_date') and c['expiry_date'] < datetime.now(timezone.utc).isoformat()), None)
    if expired:
        res = requests.post(f"{BASE_URL}/coupon/apply", json={"code": expired['coupon_code']}, headers=HEADERS)
        assert res.status_code == 400

def test_coupon_min_cart_value():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    coupons = get_admin_data("coupons")
    min_val_coupon = next((c for c in coupons if c.get('min_cart_value', 0) > 1000), None)
    if min_val_coupon:
        res = requests.post(f"{BASE_URL}/coupon/apply", json={"code": min_val_coupon['coupon_code']}, headers=HEADERS)
        assert res.status_code == 400

def test_coupon_remove():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    requests.post(f"{BASE_URL}/coupon/remove", headers=HEADERS)
    cart = requests.get(f"{BASE_URL}/cart", headers=HEADERS).json()
    assert cart.get('coupon_code') is None

# --- 8. Checkout ---
def test_checkout_empty_cart():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    res = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "COD"}, headers=HEADERS)
    assert res.status_code == 400

def test_checkout_invalid_method():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        requests.post(f"{BASE_URL}/cart/add", json={"product_id": products[0]['product_id'], "quantity": 1}, headers=HEADERS)
        res = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "INVALID"}, headers=HEADERS)
        assert res.status_code == 400

def test_checkout_cod_limit():
    requests.delete(f"{BASE_URL}/cart/clear", headers=HEADERS)
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    high_price_p = next((p for p in products if p['price'] > 1000), products[0])
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": high_price_p['product_id'], "quantity": 6}, headers=HEADERS)
    
    res = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "COD"}, headers=HEADERS)
    assert res.status_code == 400

# --- 9. Wallet ---
def test_wallet_get():
    res = requests.get(f"{BASE_URL}/wallet", headers=HEADERS)
    assert res.status_code == 200

def test_wallet_add_valid():
    res = requests.post(f"{BASE_URL}/wallet/add", json={"amount": 100}, headers=HEADERS)
    assert res.status_code == 200

def test_wallet_add_zero():
    res = requests.post(f"{BASE_URL}/wallet/add", json={"amount": 0}, headers=HEADERS)
    assert res.status_code == 400

def test_wallet_add_too_much():
    res = requests.post(f"{BASE_URL}/wallet/add", json={"amount": 100001}, headers=HEADERS)
    assert res.status_code == 400

def test_wallet_pay_valid():
    requests.post(f"{BASE_URL}/wallet/add", json={"amount": 500}, headers=HEADERS)
    res = requests.post(f"{BASE_URL}/wallet/pay", json={"amount": 10}, headers=HEADERS)
    assert res.status_code == 200

def test_wallet_pay_zero():
    res = requests.post(f"{BASE_URL}/wallet/pay", json={"amount": 0}, headers=HEADERS)
    assert res.status_code == 400

def test_wallet_pay_insufficient():
    res = requests.post(f"{BASE_URL}/wallet/pay", json={"amount": 9999999}, headers=HEADERS)
    assert res.status_code == 400

# --- 10. Loyalty ---
def test_loyalty_get():
    res = requests.get(f"{BASE_URL}/loyalty", headers=HEADERS)
    assert res.status_code == 200

def test_loyalty_redeem_valid():
    bal = requests.get(f"{BASE_URL}/loyalty", headers=HEADERS).json().get('points', 0)
    if bal >= 1:
        res = requests.post(f"{BASE_URL}/loyalty/redeem", json={"points": 1}, headers=HEADERS)
        assert res.status_code == 200

def test_loyalty_redeem_zero():
    res = requests.post(f"{BASE_URL}/loyalty/redeem", json={"points": 0}, headers=HEADERS)
    assert res.status_code == 400

def test_loyalty_redeem_insufficient():
    res = requests.post(f"{BASE_URL}/loyalty/redeem", json={"points": 9999999}, headers=HEADERS)
    assert res.status_code == 400

# --- 11. Orders ---
def test_get_orders():
    res = requests.get(f"{BASE_URL}/orders", headers=HEADERS)
    assert res.status_code == 200

def test_get_order_not_found():
    res = requests.get(f"{BASE_URL}/orders/999999", headers=HEADERS)
    assert res.status_code == 404

def test_cancel_order_not_found():
    res = requests.post(f"{BASE_URL}/orders/999999/cancel", headers=HEADERS)
    assert res.status_code == 404

def test_cancel_delivered_order_hint():
    orders = get_admin_data("orders")
    delivered = next((o for o in orders if o.get('order_status') == 'DELIVERED'), None)
    if delivered:
        user_headers = {"X-Roll-Number": "2024113003", "X-User-ID": str(delivered['user_id'])}
        res = requests.post(f"{BASE_URL}/orders/{delivered['order_id']}/cancel", headers=user_headers)
        assert res.status_code == 400, "Should reject cancellation of DELIVERED order"

def test_order_invoice_totals():
    orders = requests.get(f"{BASE_URL}/orders", headers=HEADERS).json()
    if orders:
        order = orders[0]
        res = requests.get(f"{BASE_URL}/orders/{order['order_id']}/invoice", headers=HEADERS)
        assert res.status_code == 200
        inv = res.json()
        assert round(inv['subtotal'] + inv['gst_amount'], 2) == order['total_amount']

# --- 12. Reviews ---
def test_post_review_valid():
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        res = requests.post(f"{BASE_URL}/products/{p_id}/reviews", json={"rating": 3, "comment": "Okay"}, headers=HEADERS)
        assert res.status_code in [200, 201]

def test_post_review_invalid_rating():
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        res = requests.post(f"{BASE_URL}/products/{p_id}/reviews", json={"rating": 6, "comment": "Okay"}, headers=HEADERS)
        assert res.status_code == 400
        res = requests.post(f"{BASE_URL}/products/{p_id}/reviews", json={"rating": 0, "comment": "Okay"}, headers=HEADERS)
        assert res.status_code == 400

def test_post_review_invalid_comment():
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if products:
        p_id = products[0]['product_id']
        res = requests.post(f"{BASE_URL}/products/{p_id}/reviews", json={"rating": 5, "comment": ""}, headers=HEADERS)
        assert res.status_code == 400
        res = requests.post(f"{BASE_URL}/products/{p_id}/reviews", json={"rating": 5, "comment": "A"*201}, headers=HEADERS)
        assert res.status_code == 400

def test_review_decimal_average_hint():
    products = requests.get(f"{BASE_URL}/products", headers=HEADERS).json()
    if len(products) > 1:
        p_id = products[1]['product_id']
        requests.post(f"{BASE_URL}/products/{p_id}/reviews", json={"rating": 5, "comment": "Great!"}, headers={"X-Roll-Number": "2024113003", "X-User-ID": "5"})
        requests.post(f"{BASE_URL}/products/{p_id}/reviews", json={"rating": 4, "comment": "Good"}, headers={"X-Roll-Number": "2024113003", "X-User-ID": "6"})
        
        res = requests.get(f"{BASE_URL}/products/{p_id}/reviews", headers=HEADERS)
        assert res.json().get('average_rating') == 4.5, f"Expected 4.5, got {res.json().get('average_rating')} - decimal calculation failed"

# --- 13. Support Tickets ---
def test_get_tickets():
    res = requests.get(f"{BASE_URL}/support/tickets", headers=HEADERS)
    assert res.status_code == 200

def test_post_ticket_valid():
    res = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "Help me please", "message": "I need help"}, headers=HEADERS)
    assert res.status_code in [200, 201]

def test_post_ticket_invalid_subject():
    res = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "Hi", "message": "I need help"}, headers=HEADERS)
    assert res.status_code == 400
    res = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "A"*101, "message": "I need help"}, headers=HEADERS)
    assert res.status_code == 400

def test_post_ticket_invalid_message():
    res = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "Valid Subject", "message": ""}, headers=HEADERS)
    assert res.status_code == 400
    res = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "Valid Subject", "message": "A"*501}, headers=HEADERS)
    assert res.status_code == 400

def test_put_ticket_valid_transitions():
    res = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "Valid Subject", "message": "Valid Message"}, headers=HEADERS)
    t_id = extract_id(res.json(), 'ticket_id')
    if t_id:
        req = requests.put(f"{BASE_URL}/support/tickets/{t_id}", json={"status": "IN_PROGRESS"}, headers=HEADERS)
        assert req.status_code == 200
        req = requests.put(f"{BASE_URL}/support/tickets/{t_id}", json={"status": "CLOSED"}, headers=HEADERS)
        assert req.status_code == 200

def test_put_ticket_invalid_transition():
    res = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "Valid Subject", "message": "Valid Message"}, headers=HEADERS)
    t_id = extract_id(res.json(), 'ticket_id')
    if t_id:
        req = requests.put(f"{BASE_URL}/support/tickets/{t_id}", json={"status": "CLOSED"}, headers=HEADERS)
        assert req.status_code == 400
