from json import dumps, loads
from kafka import KafkaProducer
import time
from datetime import datetime

time.sleep(10)

try:

  producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
                          value_serializer=lambda x: 
                          dumps(x).encode('utf-8'))
  
except:
  raise Exception('kafka connect error')

counter = 0

while True:

    with open("producer/sahibinden-data.json", "r") as jsonFile:
        for line in jsonFile:
        
            jsonLine = loads(line)
            jsonLine["id"] = counter
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            jsonLine["timestamp_column"] = current_time
            producer.send('sahibinden', value=jsonLine)
            print(jsonLine)

            counter+=1

        time.sleep(1)
    time.sleep(4)

