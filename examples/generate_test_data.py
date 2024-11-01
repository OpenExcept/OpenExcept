import psycopg2
from datetime import datetime, timedelta
import random
import time

# Database connection parameters
db_params = {
    "dbname": "openexcept",
    "user": "openexcept",
    "password": "openexcept",
    "host": "localhost",
    "port": "5432"
}

# Create the exception_events table if it doesn't exist
create_table_sql = """
CREATE TABLE IF NOT EXISTS exception_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    group_id TEXT,
    type TEXT,
    message TEXT
);
"""

# Sample exception types
exception_types = [
    "ValueError",
    "TypeError",
    "RuntimeError",
    "KeyError",
    "IndexError"
]

# Sample group IDs
group_ids = ["app1", "app2", "app3", "backend", "frontend"]

def generate_exception():
    return {
        "group_id": random.choice(group_ids),
        "type": random.choice(exception_types),
        "message": f"Test error message {random.randint(1, 100)}"
    }

def main():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # Create table
    cur.execute(create_table_sql)
    conn.commit()

    print("Generating exception data...")
    try:
        while True:
            # Generate 1-5 exceptions every second
            num_exceptions = random.randint(1, 5)
            
            for _ in range(num_exceptions):
                exception = generate_exception()
                cur.execute(
                    """
                    INSERT INTO exception_events (group_id, type, message)
                    VALUES (%s, %s, %s)
                    """,
                    (exception["group_id"], exception["type"], exception["message"])
                )
            
            conn.commit()
            print(f"Generated {num_exceptions} exceptions")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping data generation...")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main() 