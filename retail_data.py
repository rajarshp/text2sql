import random
import uuid
from faker import Faker
import psycopg2
from psycopg2.extras import execute_batch
from datetime import timedelta


fake = Faker()

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres.rcpmmygrfhobggbgqyux",
    password="mnEUifnWjJ5BqXqk",
    host="aws-0-us-west-1.pooler.supabase.com",
    port="6543"
)

# Initialize Faker instance
fake = Faker()

def generate_phone_number():
    """Generate a phone number with exactly 15 digits."""
    # A simple phone number format with exactly 15 digits (e.g., 123-456-7890)
    phone_number = f"{random.randint(100, 999)}-{random.randint(000, 999)}-{random.randint(1000, 9999)}"
    return phone_number

def get_unique_email():
    unique_id = str(uuid.uuid4())[:8]  # Shorten the UUID for readability
    base_email = fake.name().lower()
    return f"{base_email}{unique_id}@example.com"


# Function to populate the customers table
def populate_customers(conn):
    query = """
    INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING customer_id;
    """

    customers = [
        (
            fake.first_name(),
            fake.last_name(),
            get_unique_email(), 
            generate_phone_number(),
            fake.address()[:255],
            fake.city(),
            fake.state(),
            fake.zipcode(),
            fake.date_this_decade()
        )
        for _ in range(50)
    ]

    customer_ids = []
    with conn.cursor() as cur:
        for customer in customers:
            cur.execute(query, customer)
            customer_ids.append(cur.fetchone()[0])
    conn.commit()

    return customer_ids

# Function to populate the orders table
def populate_orders(conn, cust_ids):
    query = """
    INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address, billing_address, payment_method, transaction_id, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    orders = [
        (
            random.choice(cust_ids),
            fake.date_this_year(),
            round(random.uniform(50, 1000), 2),
            random.choice(['Pending', 'Completed', 'Cancelled']),
            fake.address()[:255],
            fake.address()[:255],
            random.choice(['Credit Card', 'PayPal', 'Bank Transfer']),
            fake.unique.uuid4()[:50],
            fake.date_this_year()
        )
        for _ in range(50)  # 50 orders
    ]
    with conn.cursor() as cur:
        execute_batch(cur, query, orders)
    conn.commit()

# Function to populate the stores table
def populate_stores(conn, employee_ids):
    query = """
    INSERT INTO stores (name, location, manager_id, phone, email, opening_date, square_footage, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    stores = [
        (
            fake.company(),
            fake.address()[:255],
            random.choice(employee_ids),
            fake.phone_number()[:15],
            fake.unique.email()[:100],
            fake.date_this_decade(),
            random.randint(1000, 10000),
            fake.date_this_decade()
        )
        for _ in range(10)  # 10 stores
    ]
    with conn.cursor() as cur:
        execute_batch(cur, query, stores)
    conn.commit()


# Function to populate the products table
def populate_products(conn):
    query = """
    INSERT INTO products (name, description, category, price, stock, sku, manufacturer, warranty_period)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING product_id;
    """

    products = [
        (
            f"{fake.word().capitalize()} {random.choice(['Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Smartwatch'])}",  # Product name
            fake.text(max_nb_chars=200),  # Description
            fake.word(),                # Category
            round(random.uniform(5, 500), 2),  # Price
            random.randint(10, 1000),   # Stock quantity
            str(uuid.uuid4())[:50],    # SKU (unique)
            fake.company()[:50],        # Manufacturer
            f"{random.randint(1, 5)} years",  # Warranty period
        )
        for _ in range(50)  # Create 50 products
    ]

    with conn.cursor() as cur:
        cur.executemany(query, products)
        conn.commit()

        # Fetch all inserted product IDs
        cur.execute("SELECT product_id FROM products;")
        product_ids = [row[0] for row in cur.fetchall()]

    return product_ids

# Function to populate the product_suppliers table
def populate_product_suppliers(conn, supplier_ids, product_ids):
    query = """
    INSERT INTO productsuppliers (product_id, supplier_id, cost_price, supply_date, batch_number)
    VALUES (%s, %s, %s, %s, %s);
    """

    productsuppliers = [
        (
            random.choice(product_ids),  # Random product_id
            random.choice(supplier_ids),  # Random supplier_id
            round(random.uniform(10, 300), 2),  # Cost price
            fake.date_this_decade(),          # Supply date
            str(uuid.uuid4())[:30],          # Batch number
        )
        for _ in range(100)  # Create 100 product-supplier relationships
    ]

    with conn.cursor() as cur:
        cur.executemany(query, productsuppliers)
        conn.commit()


# Function to populate the suppliers table
def populate_suppliers(conn):
    query = """
    INSERT INTO suppliers (name, contact_name, phone, email, address, city, state, zip_code)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING supplier_id;
    """

    suppliers = [
        (
            fake.company()[:100],  # Supplier name
            fake.name(),           # Contact name
            fake.phone_number()[:15],  # Phone number
            f"{fake.unique.first_name().lower()}.{fake.unique.last_name().lower()}@example.com",  # Email
            fake.address()[:255],  # Address
            fake.city(),           # City
            fake.state(),          # State
            fake.zipcode(),        # Zip code
        )
        for _ in range(30)  # Create 30 suppliers
    ]

    with conn.cursor() as cur:
        cur.executemany(query, suppliers)
        conn.commit()

        # Fetch all inserted supplier IDs
        cur.execute("SELECT supplier_id FROM suppliers;")
        supplier_ids = [row[0] for row in cur.fetchall()]

    return supplier_ids

# Function to populate the employees table
def populate_employees(conn):
    # Query to insert employees without manager_id
    insert_query = """
    INSERT INTO Employees (first_name, last_name, email, phone, hire_date, job_title, department, salary, manager_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
    RETURNING employee_id;
    """

    # Query to update manager_id after employees are inserted
    update_query = """
    UPDATE Employees
    SET manager_id = %s
    WHERE employee_id = %s;
    """

    # Step 1: Generate employees data without managers
    employees = [
        (
            fake.first_name(),
            fake.last_name(),
            f"{fake.first_name().lower()}.{fake.last_name().lower()}@{fake.domain_name()}",
            fake.phone_number()[:15],
            fake.date_this_decade(),
            fake.job()[:50],
            fake.company()[:50],
            round(random.uniform(30000, 120000), 2),
        )
        for _ in range(50)  # Adjust number of employees as needed
    ]

    with conn.cursor() as cur:
        # Step 2: Insert employees and collect their IDs
        cur.executemany(insert_query, employees)
        conn.commit()

        # Fetch all inserted employee IDs
        cur.execute("SELECT employee_id FROM Employees;")
        employee_ids = [row[0] for row in cur.fetchall()]

        # Step 3: Assign managers (randomly choose from existing IDs)
        managers = [
            (random.choice(employee_ids), emp_id)  # Randomly assign manager_id
            for emp_id in employee_ids
            if random.random() < 0.7  # 70% chance of having a manager
        ]

        # Step 4: Update employees to set manager_id
        cur.executemany(update_query, managers)
        conn.commit()

    return employee_ids    


# Function to populate the inventory table
def populate_inventory(conn):
    query = """
    INSERT INTO inventory (product_id, store_id, quantity, restock_level, created_at)
    VALUES (%s, %s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        
        cur.execute("SELECT store_id FROM stores;")
        store_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT product_id FROM products;")
        product_ids = [row[0] for row in cur.fetchall()]

        inventory = [
            (
                random.choice(product_ids),
                random.choice(store_ids),
                random.randint(10, 200),
                random.randint(5, 50),
                fake.date_this_year()
            )
            for _ in range(50)  # 50 inventory entries
        ]
        
        execute_batch(cur, query, inventory)
        conn.commit()

# Function to populate the sales table
def populate_sales(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT store_id FROM stores;")
        store_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT employee_id FROM employees;")
        employee_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT order_id FROM orders;")
        order_ids = [row[0] for row in cur.fetchall()]

    # Generate sales records using valid references
    query = """
    INSERT INTO sales (store_id, employee_id, order_id, sale_date, total_amount)
    VALUES (%s, %s, %s, %s, %s);
    """

    sales = [
        (
            random.choice(store_ids),  # Randomly select a store_id
            random.choice(employee_ids),  # Randomly select an employee_id
            random.choice(order_ids),  # Randomly select an order_id
            fake.date_this_year(),  # Sale date in the current year
            round(random.uniform(100, 1000), 2)  # Random sale total amount between 100 and 1000
        )
        for _ in range(100)  # Generate 100 sales records
    ]

    # Insert the sales data into the sales table
    with conn.cursor() as cur:
        cur.executemany(query, sales)
        conn.commit()

# Function to populate the product_promotions table
def populate_product_promotions(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT product_id FROM products;")
        product_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT promotion_id FROM promotions;")
        promotion_ids = [row[0] for row in cur.fetchall()]

    # Generate product-promotion records by randomly linking products with promotions
    query = """
    INSERT INTO productpromotions (product_id, promotion_id)
    VALUES (%s, %s);
    """

    product_promotions = [
        (
            random.choice(product_ids),  # Random product_id
            random.choice(promotion_ids)  # Random promotion_id
        )
        for _ in range(100)  # Assuming you want to create 100 product-promotion links
    ]

    # Insert the product-promotion data into the ProductPromotions table
    with conn.cursor() as cur:
        cur.executemany(query, product_promotions)
        conn.commit()

# Function to populate the promotions table
def populate_promotions(conn):
    query = """
    INSERT INTO promotions (name, description, discount_percentage, start_date, end_date)
    VALUES (%s, %s, %s, %s, %s);
    """

    promotions = [
        (
            fake.word().capitalize() + " Sale",  # Random promotion name like 'Spring Sale'
            fake.sentence(),  # Random description
            round(random.uniform(5, 50), 2),  # Random discount percentage between 5 and 50
            fake.date_this_year(),  # Random start date in the current year
            fake.date_this_year() + timedelta(days=random.randint(5, 30))  # Random end date 5-30 days after start
        )
        for _ in range(50)  # Assuming you want to generate 50 promotions
    ]

    # Insert the promotions data into the promotions table
    with conn.cursor() as cur:
        cur.executemany(query, promotions)
        conn.commit()

# Function to populate the customers_loyalty table
def populate_customers_loyalty(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT customer_id FROM customers;")
        customer_ids = [row[0] for row in cur.fetchall()]

    # Define tier thresholds based on points
    def assign_tier(points):
        if points < 100:
            return "Bronze"
        elif points < 500:
            return "Silver"
        elif points < 1000:
            return "Gold"
        else:
            return "Platinum"
    
    # Generate loyalty records by randomly assigning points and tiers to customers
    query = """
    INSERT INTO customersloyalty (customer_id, points, tier)
    VALUES (%s, %s, %s);
    """
    
    customers_loyalty = [
        (
            random.choice(customer_ids),  # Random customer_id
            random.randint(0, 2000),  # Random points between 0 and 2000
            assign_tier(random.randint(0, 2000))  # Assign tier based on points
        )
        for _ in range(100)  # Assuming you want to create 100 loyalty records
    ]
    
    # Insert the customers' loyalty data into the CustomersLoyalty table
    with conn.cursor() as cur:
        cur.executemany(query, customers_loyalty)
        conn.commit()

# Function to populate the support_tickets table
def populate_support_tickets(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT customer_id FROM customers;")
        customer_ids = [row[0] for row in cur.fetchall()]

    # Define some random issue descriptions
    issue_descriptions = [
        "Cannot log into my account",
        "Received damaged product",
        "Order not delivered on time",
        "Item is defective",
        "Payment failed during checkout",
        "Need assistance with product setup",
        "Refund request",
        "Account locked due to suspicious activity",
        "Request for product replacement",
        "General inquiry about the product"
    ]
    
    # Define possible statuses for tickets
    statuses = ["Open", "In Progress", "Resolved"]
    
    # Generate support ticket records
    query = """
    INSERT INTO supporttickets (customer_id, issue_description, status, resolved_at)
    VALUES (%s, %s, %s, %s);
    """
    
    support_tickets = [
        (
            random.choice(customer_ids),  # Random customer_id
            random.choice(issue_descriptions),  # Random issue description
            random.choice(statuses),  # Random status
            None if random.choice(statuses) != "Resolved" else fake.date_this_year()  # Resolved_at if status is Resolved
        )
        for _ in range(100)  # Assuming you want to create 100 support tickets
    ]
    
    # Insert the support ticket data into the SupportTickets table
    with conn.cursor() as cur:
        cur.executemany(query, support_tickets)
        conn.commit()

# Function to populate the feedback table
def populate_feedback(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT customer_id FROM customers;")
        customer_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT product_id FROM products;")
        product_ids = [row[0] for row in cur.fetchall()]

    # Define random comments for feedback
    comments_list = [
        "Great product! Will buy again.",
        "Not satisfied, the quality could be better.",
        "Good value for the price.",
        "Item was as described. Happy with my purchase.",
        "Fast delivery, but the product didn't meet my expectations.",
        "Amazing quality! Exceeded my expectations.",
        "The product is okay, but I expected more features.",
        "Fantastic experience, highly recommend!",
        "The product was damaged when it arrived.",
        "Customer support was helpful with my issue."
    ]
    
    # Generate feedback records with random data
    query = """
    INSERT INTO feedback (customer_id, product_id, rating, comments)
    VALUES (%s, %s, %s, %s);
    """
    
    feedback_data = [
        (
            random.choice(customer_ids),  # Random customer_id
            random.choice(product_ids),  # Random product_id
            random.randint(1, 5),  # Random rating between 1 and 5
            random.choice(comments_list)  # Random comment
        )
        for _ in range(100)  # Adjust number of feedback records as needed
    ]
    
    # Insert feedback data into the Feedback table
    with conn.cursor() as cur:
        cur.executemany(query, feedback_data)
        conn.commit()

# Function to populate the shipping table
def populate_shipping(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT order_id FROM orders;")
        order_ids = [row[0] for row in cur.fetchall()]

    # Define possible shipping methods
    shipping_methods = ['Standard', 'Express', 'Overnight', 'Two-Day', 'International']

    # Generate random shipping cost between 5 and 50
    def generate_shipping_cost():
        return round(random.uniform(5.00, 50.00), 2)

    # Generate random estimated and actual delivery dates
    def generate_delivery_dates():
        estimated_delivery = fake.date_this_year(after_today=True)
        actual_delivery = fake.date_this_year(after_today=True)  # Can adjust logic for earlier or later
        return estimated_delivery, actual_delivery

    # Generate shipping records
    query = """
    INSERT INTO shipping (order_id, shipping_method, tracking_number, estimated_delivery, actual_delivery, shipping_cost)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    shipping_data = [
        (
            random.choice(order_ids),  # Random order_id
            random.choice(shipping_methods),  # Random shipping method
            fake.unique.bothify(text='??-########', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),  # Unique tracking number
            *generate_delivery_dates(),  # Generate estimated and actual delivery dates
            generate_shipping_cost()  # Random shipping cost
        )
        for _ in range(100)  # Adjust the number of records as needed
    ]
    
    # Insert shipping data into the Shipping table
    with conn.cursor() as cur:
        cur.executemany(query, shipping_data)
        conn.commit()

def generate_refund_amount(product_id):
        with conn.cursor() as cur:
            cur.execute("SELECT price FROM products WHERE product_id = %s;", (product_id,))
            price = float(cur.fetchone()[0])
        return round(random.uniform(0.5, 1.0) * price, 2)

# Function to populate the returns table
def populate_returns(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT order_id FROM orders;")
        order_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT product_id FROM products;")
        product_ids = [row[0] for row in cur.fetchall()]

    # List of possible return reasons
    return_reasons = [
        'Defective product', 'Wrong item received', 'Not as described', 'Better price elsewhere', 'Changed mind', 'Arrived late', 'Product damaged'
    ]

    # Generate random refund amount based on product price (up to 100% refund)
    

    # Generate return records
    query = """
    INSERT INTO returns (order_id, product_id, return_reason, return_date, refund_amount)
    VALUES (%s, %s, %s, %s, %s);
    """
    
    return_data = [
        (
            random.choice(order_ids),  # Random order_id
            random.choice(product_ids),  # Random product_id
            random.choice(return_reasons),  # Random return reason
            fake.date_this_year(after_today=True),  # Random return date within the current year
            generate_refund_amount(random.choice(product_ids))  # Refund based on product price
        )
        for _ in range(100)  # Adjust the number of records as needed
    ]
    
    # Insert return data into the Returns table
    with conn.cursor() as cur:
        cur.executemany(query, return_data)
        conn.commit()

# Function to populate the giftcards table
def populate_giftcards(conn):
    query = """
    INSERT INTO GiftCards (customer_id, balance, expiration_date)
    VALUES (%s, %s, %s);
    """
    
    # Retrieve customer IDs (assuming you already have customers populated in the database)
    customer_ids = []
    with conn.cursor() as cur:
        cur.execute("SELECT customer_id FROM Customers;")
        customer_ids = [row[0] for row in cur.fetchall()]

    # Generate gift card data for each customer
    gift_cards = [
        (
            random.choice(customer_ids),  # Randomly pick a customer_id from existing customers
            round(random.uniform(10.0, 500.0), 2),  # Random balance between 10 and 500
            fake.date_between(start_date="today", end_date="+2y")  # Expiration date within the next 2 years
        )
        for _ in range(100)  # Adjust this value based on the desired number of gift cards
    ]
    
    # Insert the generated data into the GiftCards table
    with conn.cursor() as cur:
        execute_batch(cur, query, gift_cards)
    conn.commit()

# Function to populate the orderdetailsview table
def populate_orderdetails(conn):
    query = """
    INSERT INTO OrderDetails (order_id, product_id, quantity, unit_price, discount)
    VALUES (%s, %s, %s, %s, %s);
    """
    
    # Retrieve order IDs and product IDs (ensure orders and products exist)
    order_ids = []
    product_ids = []
    
    # Fetch order_ids from Orders table
    with conn.cursor() as cur:
        cur.execute("SELECT order_id FROM Orders;")
        order_ids = [row[0] for row in cur.fetchall()]
    
    # Fetch product_ids from Products table
    with conn.cursor() as cur:
        cur.execute("SELECT product_id FROM Products;")
        product_ids = [row[0] for row in cur.fetchall()]

    # Generate order details data (assuming we want 200 order details)
    order_details = [
        (
            random.choice(order_ids),  # Randomly pick an order_id from existing orders
            random.choice(product_ids),  # Randomly pick a product_id from existing products
            random.randint(1, 10),  # Random quantity between 1 and 10
            round(random.uniform(5.0, 100.0), 2),  # Random unit price between 5.00 and 100.00
            round(random.uniform(0.0, 20.0), 2)  # Random discount between 0.00 and 20.00
        )
        for _ in range(200)  # Adjust this value based on the number of order details needed
    ]
    
    # Insert the generated data into the OrderDetails table
    with conn.cursor() as cur:
        execute_batch(cur, query, order_details)
    conn.commit()

# Main function to connect and populate all tables
def populate_all_tables():

    cust_ids = populate_customers(conn)
    supplier_ids = populate_suppliers(conn) 
    product_ids = populate_products(conn) 
    populate_product_suppliers(conn, supplier_ids, product_ids)
    populate_orders(conn, cust_ids)
    emp_ids = populate_employees(conn)
    populate_stores(conn, emp_ids)
    populate_inventory(conn)
    populate_sales(conn)
    populate_promotions(conn)
    populate_product_promotions(conn)
    populate_customers_loyalty(conn)
    populate_support_tickets(conn)
    populate_feedback(conn)
    populate_shipping(conn)
    populate_returns(conn)
    populate_giftcards(conn)
    populate_orderdetails(conn)

    conn.close()

# Run the population process
populate_all_tables()

print("Data Generated")
