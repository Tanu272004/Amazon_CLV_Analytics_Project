import pandas as pd
import random
from faker import Faker
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Initialize Faker
fake = Faker()

# -------------------------------
# STEP 1: Generate Customers
# -------------------------------
num_customers = 500
customers = []
for i in range(1, num_customers + 1):
    customers.append({
        "customer_id": i,
        "name": fake.name(),
        "region": fake.country(),
        "signup_date": fake.date_between(start_date='-3y', end_date='today')
    })

customers_df = pd.DataFrame(customers)
# ✅ Fix date format for MySQL
customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'], errors='coerce').dt.strftime('%Y-%m-%d')

# -------------------------------
# STEP 2: Generate Products
# -------------------------------
num_products = 50
categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports']
products = []
for i in range(1, num_products + 1):
    products.append({
        "product_id": i,
        "category": random.choice(categories),
        "price": round(random.uniform(10, 500), 2)
    })

products_df = pd.DataFrame(products)

# -------------------------------
# STEP 3: Generate Orders
# -------------------------------
num_orders = 5000
orders = []
for i in range(1, num_orders + 1):
    cust_id = random.randint(1, num_customers)
    prod_id = random.randint(1, num_products)
    order_date = fake.date_between(
        start_date=pd.to_datetime(customers_df.loc[cust_id - 1, 'signup_date']),
        end_date='today'
    )
    quantity = random.randint(1, 5)
    price = products_df.loc[prod_id - 1, 'price']

    orders.append({
        "order_id": i,
        "customer_id": cust_id,
        "product_id": prod_id,
        "order_date": order_date,
        "quantity": quantity,
        "price": price
    })

orders_df = pd.DataFrame(orders)
# ✅ Fix order_date format
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'], errors='coerce').dt.strftime('%Y-%m-%d')

# -------------------------------
# STEP 4: Calculate CLV
# -------------------------------
agg_orders = orders_df.groupby('customer_id').agg({
    'quantity': 'sum',
    'price': 'mean',
    'order_id': 'count'
}).rename(columns={'price': 'avg_price', 'order_id': 'frequency'})

agg_orders['monetary'] = agg_orders['avg_price'] * agg_orders['quantity']
current_date = datetime.now()
customers_df['lifespan_years'] = customers_df['signup_date'].apply(
    lambda x: (current_date - datetime.strptime(x, '%Y-%m-%d')).days / 365
)

# Merge lifespan
agg_orders = agg_orders.merge(customers_df[['customer_id', 'lifespan_years']], on='customer_id')

# CLV Calculation
agg_orders['avg_order_value'] = agg_orders['monetary'] / agg_orders['frequency']
agg_orders['clv'] = agg_orders['avg_order_value'] * agg_orders['frequency'] * agg_orders['lifespan_years']

# -------------------------------
# STEP 5: Predict Future CLV (ML)
# -------------------------------
features = agg_orders[['avg_order_value', 'frequency', 'lifespan_years']]
target = agg_orders['clv']

X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

agg_orders['predicted_clv'] = model.predict(features)

# ✅ Keep only required columns for customer_clv.csv
clv_final = agg_orders.reset_index()[['customer_id', 'avg_order_value', 'frequency', 'lifespan_years', 'clv', 'predicted_clv']]

# -------------------------------
# STEP 6: Save All CSVs (Clean for MySQL)
# -------------------------------
customers_df[['customer_id', 'name', 'region', 'signup_date']].to_csv("customers.csv", index=False)
products_df[['product_id', 'category', 'price']].to_csv("products.csv", index=False)
orders_df[['order_id', 'customer_id', 'product_id', 'order_date', 'quantity', 'price']].to_csv("orders.csv", index=False)
clv_final.to_csv("customer_clv.csv", index=False)

print("✅ Clean CSV files generated successfully for MySQL import!")
