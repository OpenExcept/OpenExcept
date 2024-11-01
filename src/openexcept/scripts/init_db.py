import psycopg2
import os
from time import sleep

def init_db():
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn_string = (
                f"postgresql://{os.getenv('POSTGRES_USER', 'openexcept')}:"
                f"{os.getenv('POSTGRES_PASSWORD', 'openexcept')}@"
                f"{os.getenv('POSTGRES_HOST', 'localhost')}:5432/"
                f"{os.getenv('POSTGRES_DB', 'openexcept')}"
            )
            
            conn = psycopg2.connect(conn_string)
            conn.autocommit = True
            cur = conn.cursor()
            
            # Enable the vector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            cur.close()
            conn.close()
            print("Database initialized successfully")
            break
            
        except psycopg2.Error as e:
            print(f"Failed to initialize database: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in 5 seconds... (Attempt {retry_count + 1}/{max_retries})")
                sleep(5)
            else:
                raise Exception("Failed to initialize database after maximum retries")

if __name__ == "__main__":
    init_db() 