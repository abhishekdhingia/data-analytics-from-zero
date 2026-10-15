# Schema and relationships
See data_dictionary.csv for every field, and metric_rules.md for units and financial definitions.

|Table|Grain / unique key|
|---|---|
|products|One product / product_id|
|customers|One customer / customer_id|
|locations|One reporting location-channel member / location_id|
|orders|One order / order_id|
|order_items|One sale line / order_item_id|
|returns|One return event / return_id|
|inventory|One snapshot-date/location/product combination|
|targets|One month/location combination|
|calendar|One date / calendar_date|
|historical_monthly_summary|One 2024 month/location/category combination|

orders → order_items is one-to-many; products → order_items is one-to-many; order_items → returns is one-to-many. Customers may be null on orders. Every other foreign key must match. For Power BI use separate derived sales and returns facts with shared dimensions; do not directly relate the two facts many-to-many. Use sale_date for sales and return_date for returns, with separate role-playing dates or explicit cohort logic when needed. Monthly targets require separate monthly-grain modeling; suppress unsupported category breakdowns.
