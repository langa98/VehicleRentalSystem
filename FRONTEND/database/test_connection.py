from connection import get_connection


connection = get_connection()

cursor = connection.cursor()

cursor.execute("SELECT DB_NAME()")

result = cursor.fetchone()

print("Connected to database:", result[0])

connection.close()