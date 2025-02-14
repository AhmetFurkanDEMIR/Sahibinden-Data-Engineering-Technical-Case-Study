import mysql.connector
import base64
from datetime import datetime
from confluent_kafka import Consumer, KafkaException, KafkaError
import time
import json

# MySQL bağlantısı
def get_db_connection():
    conn = mysql.connector.connect(
        host="mysql_db",
        user="debezium",
        password="debezium",
        database="testdb",
        port=3306
    )
    return conn

# Kafka mesajını işleyerek UPSERT işlemi yapma
def upsert_data(payload):

    conn = get_db_connection()
    cur = conn.cursor()

    # 'before' ve 'after' verilerini alıyoruz
    before = payload.get('before')
    after = payload.get('after')
    
    if not after:
        print("No data in 'after'. Skipping update.")
        return
    
    # 'after' verisinden gerekli bilgileri çekiyoruz
    record = after
    id = record.get('id')
    title = record.get('title')
    description = record.get('description', None)
    price = record.get('price')
    seller = record.get('seller')
    created_at = record.get('created_at')
    

    created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')

    operation = payload.get('op')

    if operation == 'c':  # Create operation (Insert)
        # Insert SQL komutu
        insert_query = """
            INSERT INTO sahibinden_target_table (id, title, description, price, seller, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                title = VALUES(title),
                description = VALUES(description),
                price = VALUES(price),
                seller = VALUES(seller),
                created_at = VALUES(created_at);
        """
        cur.execute(insert_query, (id, title, description, int(price), seller, created_at))

    elif operation == 'u':  # Update operation
        # Update SQL komutu
        update_query = """
            UPDATE sahibinden_target_table
            SET title = %s, description = %s, price = %s, seller = %s, created_at = %s
            WHERE id = %s;
        """
        cur.execute(update_query, (title, description, int(price), seller, created_at, id))

    elif operation == 'd':  # Delete operation
        # Delete SQL komutu
        delete_query = "DELETE FROM sahibinden_target_table WHERE id = %s;"
        cur.execute(delete_query, (id,))

    conn.commit()

    cur.close()
    conn.close()

def process_kafka_message(message):
    # Kafka'dan gelen mesajın value'su bytes formatında
    try:
        payload = json.loads(message.decode('utf-8'))  # bytes -> str -> dict
        payload = payload.get('payload')
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return

    if payload:
        upsert_data(payload)
    else:
        print("No payload found in the Kafka message.")

# Kafka Consumer yapılandırması
consumer_config = {
    'bootstrap.servers': 'kafka:9092', 
    'group.id': 'kafka-consumer-group',
    'auto.offset.reset': 'earliest',
}

# Kafka'dan veri okuma ve işleme
def consume_messages():
    consumer = Consumer(consumer_config)
    consumer.subscribe(['mysql.testdb.sahibinden']) 

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            else:
                process_kafka_message(msg.value())
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":

    time.sleep(40)
    consume_messages()
