
-- \i text2sql/retails_db.sql
-- Create the database
CREATE DATABASE retail_db;

-- Switch to the database
\c retail_db;

-- Create tables for retail_db

-- Table: Customers
CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Products
CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10, 2),
    stock INT,
    sku VARCHAR(50) UNIQUE,
    manufacturer VARCHAR(50),
    warranty_period VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Orders
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    status VARCHAR(20),
    shipping_address VARCHAR(255),
    billing_address VARCHAR(255),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(50),
    updated_at TIMESTAMP
);

-- Table: OrderDetails
CREATE TABLE OrderDetails (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(order_id),
    product_id INT REFERENCES Products(product_id),
    quantity INT,
    unit_price DECIMAL(10, 2),
    discount DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a view for the computed column
CREATE VIEW OrderDetailsView AS
SELECT 
    order_detail_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount,
    (quantity * unit_price - discount) AS total_price,
    created_at
FROM 
    OrderDetails;

-- Table: Suppliers
CREATE TABLE Suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    contact_name VARCHAR(50),
    phone VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: ProductSuppliers
CREATE TABLE ProductSuppliers (
    product_supplier_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES Products(product_id),
    supplier_id INT REFERENCES Suppliers(supplier_id),
    cost_price DECIMAL(10, 2),
    supply_date TIMESTAMP,
    batch_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Employees
CREATE TABLE Employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    hire_date TIMESTAMP,
    job_title VARCHAR(50),
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    manager_id INT REFERENCES Employees(employee_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Stores
CREATE TABLE Stores (
    store_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(255),
    manager_id INT REFERENCES Employees(employee_id),
    phone VARCHAR(15),
    email VARCHAR(100),
    opening_date TIMESTAMP,
    square_footage INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Inventory
CREATE TABLE Inventory (
    inventory_id SERIAL PRIMARY KEY,
    store_id INT REFERENCES Stores(store_id),
    product_id INT REFERENCES Products(product_id),
    quantity INT,
    restock_level INT,
    last_restocked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Sales
CREATE TABLE Sales (
    sale_id SERIAL PRIMARY KEY,
    store_id INT REFERENCES Stores(store_id),
    employee_id INT REFERENCES Employees(employee_id),
    order_id INT REFERENCES Orders(order_id),
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Promotions
CREATE TABLE Promotions (
    promotion_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    discount_percentage DECIMAL(5, 2),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: ProductPromotions
CREATE TABLE ProductPromotions (
    product_promotion_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES Products(product_id),
    promotion_id INT REFERENCES Promotions(promotion_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: CustomersLoyalty
CREATE TABLE CustomersLoyalty (
    loyalty_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(customer_id),
    points INT DEFAULT 0,
    tier VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: SupportTickets
CREATE TABLE SupportTickets (
    ticket_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(customer_id),
    issue_description TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Table: Feedback
CREATE TABLE Feedback (
    feedback_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(customer_id),
    product_id INT REFERENCES Products(product_id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Shipping
CREATE TABLE Shipping (
    shipping_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(order_id),
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(50),
    estimated_delivery TIMESTAMP,
    actual_delivery TIMESTAMP,
    shipping_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Returns
CREATE TABLE Returns (
    return_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(order_id),
    product_id INT REFERENCES Products(product_id),
    return_reason TEXT,
    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    refund_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: GiftCards
CREATE TABLE GiftCards (
    gift_card_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(customer_id),
    balance DECIMAL(10, 2),
    issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiration_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
