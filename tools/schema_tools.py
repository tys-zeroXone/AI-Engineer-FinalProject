DATABASE_SCHEMA_TEXT = """
Table: customers
- customer_unique_id (TEXT)
- customer_zip_code_prefix (INTEGER)
- customer_city_clean (TEXT)
- customer_state (TEXT)
- customer_order_count (INTEGER)
- is_repeat_customer (INTEGER)

Table: geolocation
- geolocation_zip_code_prefix (INTEGER)
- geolocation_lat (REAL)
- geolocation_lng (REAL)
- geolocation_city (TEXT)
- geolocation_state (TEXT)
- geolocation_record_count (INTEGER)

Table: order_items
- order_id (TEXT)
- order_item_id (INTEGER)
- product_id (TEXT)
- seller_id (TEXT)
- shipping_limit_date (TEXT)
- price (REAL)
- freight_value (REAL)
- flag_zero_price (INTEGER)
- flag_price_outlier (INTEGER)
- total_item_value (REAL)
- freight_ratio (REAL)
- flag_high_freight (INTEGER)

Table: orders
- order_id (TEXT)
- customer_id (TEXT)
- order_status (TEXT)
- order_purchase_timestamp (TEXT)
- order_approved_at (TEXT)
- order_delivered_carrier_date (TEXT)
- order_delivered_customer_date (TEXT)
- order_estimated_delivery_date (TEXT)
- is_approved (INTEGER)
- is_shipped (INTEGER)
- is_delivered (INTEGER)
- order_stage (TEXT)
- flag_carrier_before_approval (INTEGER)
- flag_customer_before_carrier (INTEGER)
- approval_delay_hours (REAL)
- shipping_delay_days (REAL)
- delivery_days (REAL)
- estimated_delivery_days (REAL)
- delivery_delay_days (REAL)
- is_late_delivery (REAL)
- purchase_year (INTEGER)
- purchase_month (INTEGER)
- purchase_day (INTEGER)
- purchase_hour (INTEGER)
- purchase_weekday (TEXT)
- flag_inconsistent_status_delivery (INTEGER)
- flag_canceled_but_delivered (INTEGER)

Table: payment_order
- order_id (TEXT)
- payment_value_total (REAL)
- payment_value_mean (REAL)
- payment_value_max (REAL)
- payment_installments_max (INTEGER)
- payment_installments_mean (REAL)
- payment_count (INTEGER)
- payment_type_main (TEXT)
- payment_type_nunique (INTEGER)
- flag_multi_payment (INTEGER)
- payment_boleto_count (INTEGER)
- payment_credit_card_count (INTEGER)
- payment_debit_card_count (INTEGER)
- payment_not_defined_count (INTEGER)
- payment_voucher_count (INTEGER)

Table: products
- product_id (TEXT)
- product_category_name (TEXT)
- product_name_length (REAL)
- product_description_length (REAL)
- product_photos_qty (REAL)
- product_weight_g (REAL)
- product_length_cm (REAL)
- product_height_cm (REAL)
- product_width_cm (REAL)
- product_volume_cm3 (REAL)
- product_density_g_cm3 (REAL)
- flag_unknown_category (INTEGER)
- product_category_name_english (TEXT)

Table: review_orders
- review_id (TEXT)
- order_id (TEXT)
- review_score (INTEGER)
- review_comment_title (TEXT)
- review_comment_message (TEXT)
- review_creation_date (TEXT)
- review_answer_timestamp (TEXT)
- flag_invalid_score (INTEGER)
- has_comment (INTEGER)
- review_length (INTEGER)
- flag_long_review (INTEGER)
- review_sentiment (TEXT)
- is_satisfied (INTEGER)

Table: sellers
- seller_id (TEXT)
- seller_zip_code_prefix (INTEGER)
- seller_city (TEXT)
- seller_state (TEXT)
- seller_city_clean (TEXT)
- flag_invalid_state (INTEGER)
- seller_region (TEXT)
- flag_missing_geo_info (INTEGER)

Key joins:
- orders.order_id = order_items.order_id
- orders.order_id = payment_order.order_id
- orders.order_id = review_orders.order_id
- order_items.product_id = products.product_id
- order_items.seller_id = sellers.seller_id
- customers.customer_unique_id = orders.customer_id
"""


def detect_intent(question: str) -> str:
    q = question.lower()

    recommendation_keywords = [
        "recommend", "recommendation", "what should", "action plan", "improve",
        "optimize", "strategy", "what can we do"
    ]
    rootcause_keywords = [
        "why", "root cause", "diagnose", "driver", "cause", "reason", "investigate"
    ]
    rag_keywords = [
        "explain", "definition", "what does", "meaning", "schema", "table", "join",
        "how is", "what is late delivery", "what is freight ratio"
    ]

    if any(k in q for k in recommendation_keywords):
        return "recommendation"
    if any(k in q for k in rootcause_keywords):
        return "rootcause"
    if any(k in q for k in rag_keywords):
        return "rag"
    return "sql"