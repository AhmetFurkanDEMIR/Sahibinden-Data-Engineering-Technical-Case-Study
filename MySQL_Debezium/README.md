# **1.a.** 
### **Localinizde kuracağınız bir mysqli debezium mysql connector ile dinleyip, mysql loglarını kafka topicslerinde gösterecek şekilde bir akış oluşturur musunuz?**

## **Mimari**

![mimari](/readme_images/1_mimari.png)


## Uygulamayı çalıştırma

MySQL_Debezium projesine ilerleyin

```yaml
cd MySQL_Debezium
```

docker compose up komutunu terminalde çalıştırın ve projenin ayağa kalmasını bekleyin (25 Sn)

```yaml
docker compose up
```

Eğer ilk kez çalıştırıyorsanız, Docker Hub üzerinden ihtiyaç duyulan imajlar bir defaya mahsus lokal bilgisayarınıza çekilecektir.

[MySQL DockerHub](https://hub.docker.com/_/mysql)

[Kafka DockerHub](https://hub.docker.com/r/bitnami/kafka)

[KafkaUI DockerHub](https://hub.docker.com/r/provectuslabs/kafka-ui)

[Debezium DockerHub](https://hub.docker.com/r/debezium/connect)

![debezium_docker_run](/readme_images/debezium_docker_run.png)

Oluşan "mysql-sahibinden-connector" adındaki connectoru görmek için aşağıdaki linke tıklayınız.

[http://0.0.0.0:8083/connectors/mysql-sahibinden-connector](http://0.0.0.0:8083/connectors/mysql-sahibinden-connector)

![debezium_connector](/readme_images/debezium_connector.png)

Ardından, aşağıdaki KafkaUI servisine giderek Debezium'un MySQL'den algıladığı değişiklikleri yazdığı Kafka topiğini inceleyiniz.

[http://0.0.0.0:8089/ui/clusters/kafka/all-topics/mysql.testdb.sahibinden/messages?keySerde=String&valueSerde=String&limit=100](http://0.0.0.0:8089/ui/clusters/kafka/all-topics/mysql.testdb.sahibinden/messages?keySerde=String&valueSerde=String&limit=100)

[Veri akışını canlı olarak izlemek için](http://0.0.0.0:8089/ui/clusters/kafka/all-topics/mysql.testdb.sahibinden/messages?filterQueryType=STRING_CONTAINS&attempt=2&limit=100&page=0&seekDirection=TAILING&keySerde=String&valueSerde=String&seekType=LATEST)

![kafka_ui_debezium.png](/readme_images/kafka_ui_debezium.png)


## Uygulamanın çalışma adımları

* **1-)** MySQL servisinin deploy edilmesi
* **2-)** Kafka'nın tek broker olarak deploy edilmesi
* **3-)** Kafka ve KafkaUI servislerinin bağlantı kurması.
* **4-)** Debezium'un deploy edilmesi ve Kafka ile bağlantısı
* **5-)** data-generator ile sahibinden adında tablo oluşturulması ve saniyede bir veri insert edilmesi
* **6-)** create-debezium-connector ile Debezium'da yeni bir connector oluşturma.
* **7-)** Data-generator verileri MySQL'e yazarken, Debezium bu verileri MySQL'den CDC (Change Data Capture) aracılığıyla yakalayıp Kafka'ya produce etmektedir. Kullanıcı, bu verileri KafkaUI ile consume ederek projeyi inceleyebilmektedir.

## Mimariyi inceleme ve açıklamalar


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


### **create-debezium-connector**

```yaml
create-debezium-connector:
    image: curlimages/curl:latest
    container_name: create-debezium-connector
    depends_on:
      - debezium
    entrypoint: ["sh", "-c", "sleep 25 && curl -X POST http://debezium_connect:8083/connectors/ -H 'Content-Type: application/json' -d '{\"name\": \"mysql-sahibinden-connector\", \"config\": {\"connector.class\": \"io.debezium.connector.mysql.MySqlConnector\", \"tasks.max\": \"1\", \"database.hostname\": \"mysql_db\", \"database.port\": \"3306\", \"database.user\": \"root\", \"database.password\": \"root\", \"database.server.id\": \"184054\", \"database.server.name\": \"mysql_server\", \"database.whitelist\": \"testdb\", \"database.history.kafka.bootstrap.servers\": \"kafka:9092\", \"database.history.kafka.topic\": \"dbhistory.fullfillment\", \"table.whitelist\": \"testdb.sahibinden\", \"database.history.producer.bootstrap.servers\": \"kafka:9092\", \"database.history.producer.topic\": \"dbhistory\", \"topic.prefix\": \"mysql\", \"schema.history.internal.kafka.bootstrap.servers\": \"kafka:9092\", \"schema.history.internal.kafka.topic\": \"dbhistory.schema\"} }'"]
    networks:
      - bigdata-network
```

create-debezium-connector imajı sayesinde, kendi uygulamam için yapılandırılmış JSON dosyasını debezium_connect:8083 adresine POST yöntemiyle göndererek yeni bir Debezium connector oluşturmayı sağlıyorum.

```json
{
  "name": "mysql-sahibinden-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "mysql_db",
    "database.port": "3306",
    "database.user": "root",
    "database.password": "root",
    "database.server.id": "184054",
    "database.server.name": "mysql_server",
    "database.whitelist": "testdb",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "dbhistory.fullfillment",
    "table.whitelist": "testdb.sahibinden",
    "database.history.producer.bootstrap.servers": "kafka:9092",
    "database.history.producer.topic": "dbhistory",
    "topic.prefix": "mysql",
    "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
    "schema.history.internal.kafka.topic": "dbhistory.schema"
  }
}
```

- name: Connector'ın adı. Bu örnekte "mysql-sahibinden-connector".

- connector.class: Kullanılacak Debezium connector tipi. Burada MySQL için io.debezium.connector.mysql.MySqlConnector kullanılıyor.

- tasks.max: Maksimum paralel görev sayısı. 

- database.hostname: Veritabanı sunucusunun adresi. 

- database.port: MySQL veritabanının portu. Varsayılan olarak 3306 kullanılır.

- database.user: Veritabanı bağlantısı için kullanıcı adı.

- database.password: Veritabanı kullanıcı şifresi.

- database.server.id: Veritabanı sunucusunun benzersiz ID'si.

- database.server.name: Kafka topic prefix'i olarak kullanılacak sunucu adı.

- database.whitelist: İzlenecek veritabanları. Burada yalnızca "testdb" veritabanı izleniyor.

- database.history.kafka.bootstrap.servers: Kafka sunucusunun adresi.

- database.history.kafka.topic: Veritabanı geçmişi bilgilerini saklayacak Kafka topic adı.

- table.whitelist: İzlenecek tablo. Bu örnekte "testdb.sahibinden" tablosu izlenecek.

- database.history.producer.bootstrap.servers: Kafka'ya bağlanacak olan producer'ın sunucu adresi.

- database.history.producer.topic: Veritabanı geçmişi için kullanılan Kafka topic adı.

- topic.prefix: Kafka topic adı için ön ek. Bu örnekte "mysql"

- schema.history.internal.kafka.bootstrap.servers: Schema geçmişi için Kafka sunucusu.

- schema.history.internal.kafka.topic: Schema geçmişi için Kafka topic adı.


# **1.b.** 
### **Buradaki kafka topiclerinde girilen mysql-debezium mesajlarını bir structured DB'ye nasıl upset/merge etmeyi düşünürsünüz, kırılma yaşayacabileceğimiz noktalar nereleri olur, çözüm yaklaşımlarınızı paylaşabilir misiniz? Sözel/text cevap veriniz.**

* **1.b.1** Buradaki kafka topiclerinde girilen mysql-debezium mesajlarını bir structured DB'ye nasıl upset/merge etmeyi düşünürsünüz:

Flink veya Spark kullanarak bu işlemi yapardım. Öncelikle, veri boyutuma göre bir Kubernetes kümesi oluşturur ve bunun üzerinde Jobmanager/Taskmanager yapılandırmaları tamamlanmış bir Flink kümesi deploy ederdim.

Ardından, Python veya Scala programlama dilleri ile Debezium'un aktardığı JSON verisini Kafka topic'inden çekip parçalardım ve geriye kalan anlamlı veriyi upsert/merge işlemlerine uygun hale getirip hedef veritabanında insert/update/delete işlemlerini gerçekleştirirdim. Bahsettiğim örneğe benzer şekilde bu JSON verisini Kafka'dan çekip anlamlı hale getirip, daha sonra hedef veritabanına aktarmak için basit bir Python betiği oluşturdum ([upsert_merge.py](/MySQL_Debezium/upsert_merge.py)). Bu betiği Flink'e uyarlayıp paralel bir şekilde çalıştırmayı hedeflerdim.

Aşağıdaki resimde, yine aynı veritabanasında farklı bir tabloya upsert/merge işlemi sonucunda verilerin yazıldığını görebilirsiniz.
![upsert_merge](/readme_images/upsert_merge.png)

```yaml
  upsert_merge:
    image: python:3.9
    container_name: upsert_merge
    volumes:
      - ./upsert_merge.py:/app/upsert_merge.py
    command: >
      bash -c "pip install kafka-python mysql-connector-python confluent-kafka && python /app/upsert_merge.py"
    depends_on:
      - mysql
      - kafka
    networks:
      - bigdata-network
```

* **1.b.2** Kırılma yaşayacabileceğimiz noktalar nereleri olur, çözüm yaklaşımlarınızı paylaşabilir misiniz? Sözel/text cevap veriniz.

Kırılma/kesinti yaşayabileceğimi düşündüğüm üç nokta var

**1-) Veritabanı kesintisi:** Hedef veritabanında, yani Debezium'un bağlandığı veritabanında bir kesinti olursa, bu durum benden kaynaklanmadığı için çözüm için DB yöneticileriyle iletişime geçerim. Kesinti tespiti için Prometheus ve Grafana üzerinden alert mailleri oluşturup, daha hızlı bir şekilde reaksiyon alabiliriz.

**2-) Debezium kesintisi:** Kesintisiz veri akışı sağlamak için Debezium'u, veri boyutuna göre bir cluster olarak yapılandırır, CPU, RAM ve JVM ayarlarını optimize ederek deploy ederdim. Eğer veri hacmi çok büyükse, Flink CDC ile de cluster şeklinde denemeler yaparak performansı arttırmaya çalışırdım.

Ancak, Debezium bir kesinti yaşarsa ve yeniden başlatılırsa, MySQL binlog kullanarak en son okunan offset bilgisi ile kaldığı yerden veri okumaya devam eder. Bu işlem, Debezium'un veritabanındaki her değişiklik için binlog position bilgisini takip etmesi sayesinde mümkün olur. Binlog position, veritabanındaki her işlemi sırasıyla kaydeder ve Debezium, bu konumu okuyarak işlem sırasını korur. Kesinti sonrasında, bu bilgilere dayalı olarak Debezium, veri kaybı olmadan doğru noktadan işlemlere devam eder. Bu yöntem, yüksek güvenilirlik ve veri bütünlüğü sağlar.

**3-) Flink kesintisi:** Flink servisinin kesilip tekrar başlaması durumunda, Checkpointing yapılandırması yaparak, hata durumunda geri dönüp kaldığı yerden devam etmesini sağlardım. Ayrıca, verinin hatalı işlenmesi veya bir kesinti sonrasında tekrar işlenmesini önlemek için Exactly-once Semantics kullanırdım. Bu sayede verinin doğru ve sıralı bir şekilde işlenmesini garanti altına alırdım.
