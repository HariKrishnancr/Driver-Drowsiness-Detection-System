import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'database': 'drowsiness_detection',
    'user': 'root',
    'password': ''
}

def check_db():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("--- Drivers Table ---")
        cursor.execute("SELECT * FROM drivers")
        drivers = cursor.fetchall()
        for d in drivers:
            print(d)
            
        print("\n--- Users Table ---")
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        for u in users:
            print(u)
            
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
