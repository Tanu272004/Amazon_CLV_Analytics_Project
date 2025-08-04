Create Database amazon_clv_project;
USE amazon_clv_project;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    region VARCHAR(100),
    signup_date DATE 
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    category VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    order_date DATE,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE customer_clv (
    customer_id INT,
    avg_order_value DECIMAL(10,2),
    frequency INT,
    lifespan_years DECIMAL(10,2),
    clv DECIMAL(12,2),
    predicted_clv DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

SELECT DISTINCT customer_id FROM orders
WHERE customer_id NOT IN (SELECT customer_id FROM customers);

SELECT DISTINCT product_id FROM orders
WHERE product_id NOT IN (SELECT product_id FROM products);

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE customer_clv;
TRUNCATE TABLE orders;
TRUNCATE TABLE products;
TRUNCATE TABLE customers;

SET FOREIGN_KEY_CHECKS = 1;


-- Query Part

-- 1):  Overall Average CLV  

Select Round(avg(clv),2) as Avg_CustomerCLV
From customer_clv;

--  Top 10 High-Value Customers
SELECT c.customer_id, c.name, customer_clv.clv
FROM customer_clv 
JOIN customers c ON c.customer_id = customer_clv.customer_id
ORDER BY customer_clv.clv DESC
LIMIT 10;

-- Revenue by region
SELECT c.region, ROUND(SUM(o.quantity * o.price), 2) AS total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_revenue DESC;

--  Customer Segmentation by CLV
SELECT c.customer_id, c.name, Round((customer_clv.clv),2) as CLV
FROM customer_clv 
JOIN customers c ON c.customer_id = customer_clv.customer_id
ORDER BY CLV DESC
LIMIT 10;

-- Avg order value by category;
SELECT 
    p.category,
    ROUND(AVG(o.price * o.quantity), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_order_value DESC;