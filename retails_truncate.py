import psycopg2

# PostgreSQL connection details
conn = psycopg2.connect(
    dbname="retail_db",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

try:
    # Disable foreign key checks
    cursor.execute("SET session_replication_role = 'replica';")

    # Generate truncate statements for all tables
    cursor.execute("""
        SELECT 'TRUNCATE TABLE "' || table_schema || '"."' || table_name || '" CASCADE;' 
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    truncate_statements = cursor.fetchall()

    # Execute each truncate statement
    for statement in truncate_statements:
        cursor.execute(statement[0])

    # Enable foreign key checks
    cursor.execute("SET session_replication_role = 'origin';")
    
    conn.commit()
    print("All tables truncated successfully.")
except Exception as e:
    conn.rollback()
    print("Error truncating tables:", e)
finally:
    cursor.close()
    conn.close()
