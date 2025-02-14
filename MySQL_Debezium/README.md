#### **1.a.** Localinizde kuracağınız bir mysqli debezium mysql connector ile dinleyip, mysql loglarını kafka topicslerinde gösterecek şekilde bir akış oluşturur musunuz? 

## **Mimari**

![mimari](/readme_images/1_mimari.png)


## Uygulamayı çalıştırma


```yaml
docker compose up
```


## Mimari servislerini inceleme ve açıklamalar


### **Volume ve network**

```yaml
networks:
  bigdata-network:
    driver: bridge

volumes:
  mysql_data:
    driver: local
```

Yukarıdaki yaml dosyasında okunacağı üzere tüm servislerin sağlıklı çalışabilmesi için bigdata-network adında bir network tanımlanmıştır.

mysql servisi içinde mysql_data adında bir volume tanımlanmıştır, böylece mysql servisi restart olsa bile tablolar ve veriler kaybolmayacaktır.


### **MySQL**

```yaml
mysql:
    image: mysql:8.0
    container_name: mysql_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
      MYSQL_USER: debezium
      MYSQL_PASSWORD: debezium
    ports:
      - "3306:3306"
    command: --default-authentication-plugin=mysql_native_password --server-id=1 --log-bin=mysql-bin --binlog-format=ROW --binlog-row-image=FULL
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - bigdata-network
```

Yukarıda mysql servisinin yapılandırmasını görebilirsiniz. Mysql docker imajını kullanarak 3306 portundan servisi ayağa kaldırmaktadır.

```yaml
command: --default-authentication-plugin=mysql_native_password --server-id=1 --log-bin=mysql-bin --binlog-format=ROW --binlog-row-image=FULL
```

Bu command ile mysql de bulunan testdb için CDC aktif hale getirmektedir.

- MySQL host: 0.0.0.0:3306
- MySQL DB: testdb
- MySQL Root user: root
- MySQL Root password: root
- MySQL user: debezium
- MySQL password: debezium


### **Kafka**

```yaml
kafka:
    image: docker.io/bitnami/kafka:3.6
    restart: always
    container_name: kafka
    hostname: kafka
    ports:
      - 9092:9092
      - 9093:9093
    environment:
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
    networks:
      - bigdata-network
```

Yukarıdaki yaml dosyasından anlaşılacağı üzere 9092 portundan dışarıya bir brokerlı kafka servisi deploy edilmiştir.

Broker adresleri:
- 0.0.0.0:9092
- kafka:9092


### **KafkaUI**

```yaml
kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    depends_on:
      - kafka
    ports:
      - 8089:8080
    environment:
      KAFKA_CLUSTERS_0_NAME: kafka
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      DYNAMIC_CONFIG_ENABLED: 'true'
    networks:
      - bigdata-network
    restart: on-failure
```

KafkaUI servisi kafka brokerı olan kafka:9092 ile iletişim kurarak tüm topicleri ve mesajları çeker, bu verileri web üzerinden daha rahat ve kolay görmeye olanak sağlar.

KafkaUI Link: [http://0.0.0.0:8089](http://0.0.0.0:8089)


### **Debezium**

```yaml
debezium:
    image: debezium/connect:3.0.0.Final
    container_name: debezium_connect
    restart: always
    depends_on:
      - kafka
      - mysql
    environment:
      BOOTSTRAP_SERVERS: kafka:9092
      GROUP_ID: 1
      CONFIG_STORAGE_TOPIC: debezium_configs
      OFFSET_STORAGE_TOPIC: debezium_offsets
      STATUS_STORAGE_TOPIC: debezium_status
    ports:
      - "8083:8083"
    networks:
      - bigdata-network
```

Debezium, gerçek zamanlı veri değişikliklerini (change data capture - CDC) izlemek ve aktarmak için kullanılan açık kaynaklı bir araçtır. Veritabanlarındaki değişiklikleri (ekleme, güncelleme, silme) izler ve bu değişiklikleri Kafka gibi mesajlaşma sistemlerine ileterek, veri entegrasyonu ve analizi süreçlerini kolaylaştırır. Genellikle mikro hizmetler, veri göletleri ve veri ambarları için kullanılır.

Debezium servisi 8083 portundan dışarıya açacak şekilde deploy edilmiştir.

[http://0.0.0.0:8083/](http://0.0.0.0:8083/)


### **data-generator**


```yaml
data-generator:
    image: python:3.9
    container_name: data_generator
    volumes:
      - ./data_generator.py:/app/data_generator.py
      - ./init.sql:/app/init.sql
    command: >
      bash -c "pip install mysql-connector-python && pip install sqlparse && python /app/data_generator.py"
    depends_on:
      - mysql
    networks:
      - bigdata-network
```

Data generator, otomatik bir şekilde mysql içinde sahibinden adında bir tablo oluşturur ve bu tabloya saniyede bir veri insert eder.

[Tablo oluşturma sql komutları](/MySQL_Debezium/init.sql)

[Python ile saniyede bir veri insert etme scripti](/MySQL_Debezium/data_generator.py)