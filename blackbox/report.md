# QuickCart API Black-Box Testing Report

## Test Case Design Methodology
A comprehensive suite of 77 automated test cases was engineered using `pytest` and `requests`. The tests were designed to stress the API across five core vectors:

1. **Valid Requests (Happy Path):** - *Scenario:* Retrieve active products, add valid quantities to cart, process wallet payments.
   - *Justification:* Establishes the baseline functionality of the API to ensure standard user flows are operational.
2. **Missing Fields & Headers:** - *Scenario:* Issue a `GET /api/v1/profile` request without the `X-Roll-Number` header.
   - *Expected:* 401 Unauthorized.
   - *Justification:* Validates global authentication and prevents unauthorized access to sensitive endpoints.
3. **Invalid Inputs & Wrong Data Types:** - *Scenario:* Update Profile with a 9-digit phone number or alphabetical characters.
   - *Expected:* 400 Bad Request.
   - *Justification:* Ensures strict database validation rules (e.g., exactly 10 digits) cannot be bypassed via raw API requests.
4. **Boundary Values:** - *Scenario:* Add an item to the cart with `quantity: 0`.
   - *Expected:* 400 Bad Request.
   - *Justification:* Validates that lower-bound rules are enforced to prevent non-sensical or negative cart states.
5. **Business Logic & State Machine Constraints:** - *Scenario:* Attempt to cancel an order with the status `DELIVERED`.
   - *Expected:* 400 Bad Request.
   - *Justification:* Verifies the lifecycle state machine prevents the backward traversal of completed orders.

---

## Comprehensive Bug Reports
During the automated execution, 8 critical vulnerabilities and logical flaws were discovered in the QuickCart server. 

### Bug 1: Phone Number Type Validation Failure
- **Endpoint tested:** `PUT /api/v1/profile`
- **Request payload:** - Method: `PUT`
  - URL: `/api/v1/profile`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
  - Body: `{"name": "Valid", "phone": "abcdefghij"}`
- **Expected result:** 400 Bad Request (phone must be exactly 10 digits, not alphabetical characters).
- **Actual result observed:** 200 OK. The server accepted alphabetical characters into a numeric field.

### Bug 2: Address Field Immutability Bypass
- **Endpoint tested:** `PUT /api/v1/addresses/{address_id}`
- **Request payload:** - Method: `PUT`
  - URL: `/api/v1/addresses/1`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
  - Body: `{"street": "New St Updated", "is_default": true}`
- **Expected result:** 200 OK, with the response reflecting the street updated to "New St Updated".
- **Actual result observed:** 200 OK, but the server completely ignored the field update. The street data remained unchanged ("Immutable St").

### Bug 3: Lower-Bound Cart Quantity Failure
- **Endpoint tested:** `POST /api/v1/cart/add`
- **Request payload:** - Method: `POST`
  - URL: `/api/v1/cart/add`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
  - Body: `{"product_id": 1, "quantity": 0}`
- **Expected result:** 400 Bad Request (Quantity must be at least 1).
- **Actual result observed:** 200 OK. The server allows adding 0 (or negative) items to the cart.

### Bug 4: Cart Total Mathematical Omission
- **Endpoint tested:** `GET /api/v1/cart`
- **Request payload:** - Method: `GET`
  - URL: `/api/v1/cart`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
- **Expected result:** The `total` field explicitly sums all product subtotals (Expected: 630).
- **Actual result observed:** Mathematical failure. The server returned a corrupted total (`-16` instead of `630`), indicating an iteration bug that skips or corrupts the final cart item.

### Bug 5: Coupon Maximum Cap Logic Failure
- **Endpoint tested:** `POST /api/v1/coupon/apply`
- **Request payload:** - Method: `POST`
  - URL: `/api/v1/coupon/apply`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
  - Body: `{"code": "PERCENT_COUPON_WITH_CAP"}`
- **Expected result:** 200 OK, with the discount successfully applied but scaled down/capped at the coupon's `max_discount` limit.
- **Actual result observed:** 400 Bad Request. The server rejects the coupon application entirely rather than capping the percentage discount.

### Bug 6: Cash-On-Delivery Limit Bypass
- **Endpoint tested:** `POST /api/v1/checkout`
- **Request payload:** - Method: `POST`
  - URL: `/api/v1/checkout`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
  - Body: `{"payment_method": "COD"}`
- **Expected result:** 400 Bad Request (COD is strictly not allowed for orders > 5000).
- **Actual result observed:** 200 OK. The server allowed a massive order to be checked out via COD.

### Bug 7: Review Rating Upper-Bound Failure
- **Endpoint tested:** `POST /api/v1/products/{product_id}/reviews`
- **Request payload:** - Method: `POST`
  - URL: `/api/v1/products/1/reviews`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
  - Body: `{"rating": 6, "comment": "Okay"}`
- **Expected result:** 400 Bad Request (Ratings must be strictly between 1 and 5).
- **Actual result observed:** 200 OK. The server accepted an out-of-bounds rating.

### Bug 8: Review Average Decimal Calculation Flaw
- **Endpoint tested:** `GET /api/v1/products/{product_id}/reviews`
- **Request payload:** - Method: `GET`
  - URL: `/api/v1/products/2/reviews`
  - Headers: `{"X-Roll-Number": "2024113003", "X-User-ID": "1"}`
- **Expected result:** The `average_rating` calculates to a proper decimal (e.g., `4.5`).
- **Actual result observed:** Calculation error. The server returned an unformatted, floating-point calculation (`4.142857142857143`) instead of the correct weighted decimal average.