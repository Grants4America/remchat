import mysql.connector

# Establish connection to the database
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='oluwasegun137',
            database='remgram'
        )

        if conn.is_connected():
            print("Connected to remgram database 👍")
            return conn
        else:
            print("Error occurred! 😒")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
