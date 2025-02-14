import time
import mysql.connector
import sqlparse
from datetime import datetime

time.sleep(25)

conn = mysql.connector.connect(
    host="mysql_db",
    user="debezium",
    password="debezium",
    database="testdb"
)
cursor = conn.cursor()

create_table_query = open("/app/init.sql", "r", encoding="utf-8")
create_table_query = create_table_query.read()

statements = sqlparse.split(create_table_query)
for statement in statements:
    if statement.strip():
        cursor.execute(statement)
conn.commit()

while True:
    title = f"Ürün {int(time.time())}"
    description = "Test Aciklama"
    seller = "Test Satıcı"
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    query = "INSERT INTO sahibinden (title, description, price, seller, created_at) VALUES (%s, %s, 100, %s, %s)"
    values = (title, description, seller, created_at)

    cursor.execute(query, values)
    conn.commit()

    print(f"Veri eklendi: {title}")
    time.sleep(1)

cursor.close()
conn.close()