# **3.a.** 
### **Apache Flink ile Kafka entegrasyonu yapıp, Kafka'dan JSON veri okuyup bu veriyi bazı hesaplamalar yaptıktan sonra 2 dakikada bir sonucu  local dosya sistemine csv olarak yazan pipeline oluşturun, örnek implementasyon yapar mısınız?**

## **Mimari**

![flink_kafka_mimari](/readme_images/flink_kafka_mimari.png)

## Uygulamayı çalıştırma

Flink_Kafka projesine ilerleyin

```yaml
cd Flink_Kafka
```

docker compose up komutunu terminalde çalıştırın ve projenin ayağa kalmasını bekleyin (20 Sn)

```yaml
docker compose up

# or docker-compose up
```

![flink_kafka_composeup](/readme_images/flink_kafka_composeup.png)

Eğer ilk kez çalıştırıyorsanız, Docker Hub üzerinden ihtiyaç duyulan imajlar bir defaya mahsus lokal bilgisayarınıza çekilecektir.

[Kafka DockerHub](https://hub.docker.com/r/bitnami/kafka)

[Apache Flink DockerHub](https://hub.docker.com/_/flink)

Docker imajları otomatik olarak ayağa kalkıp işlemleri başlatacaktır.

İlk olarak Kafka tek broker olarak ayağa kalkar ver ![](/Flink_Kafka/producer/kafka_producer.py) python scripti ile Kafka'ya veri yazar.

[KafkaUI](http://0.0.0.0:8089/ui/clusters/kafka/all-topics?perPage=25)

![](/readme_images/flink_kafka_ui.png)

Ardından Flink jobmanager ve taskmanager ayağa kalkar ve birbirleriyle iletişim kurarak bir cluster oluşturur.

![flink_ui](/readme_images/flink_ui.png)

Son olarak Flink Submitter adlı container [flink-submit.py](/Flink_Kafka/flink-submit.py) Python scriptini run komutu ile Jobmanager'a iletir ve job'u başlatır.

![flink_running_job](/readme_images/flink_running_job.png)

Yukarıdaki resimde görüleceği üzere Job'un başladığını ve running durumunda olduğunu görebilirsiniz.

Job başladıktan sonra otomatik olarak [/Flink_Kafka/out_data/](/Flink_Kafka/out_data/) klasörü altında .part-xxxx adında dosya oluşacaktır.

![file_output](/readme_images/file_output.png)

Bu dosyanın içerisinde csv formatına uygun olarak "," ile ayrılmış ve işlem görmüş verileri görebilirsiniz.

![part_data](/readme_images/part_data.png)

girdi veri:

```json
{
	"id": 7,
	"product": "Televizyon",
	"description": "ikinci el LG OLED TV",
	"price": 18000,
	"kdv": 0.18,
	"timestamp_column": "2025-02-16 07:29:49"
}
```

çıktı veri:

```csv
7,Televizyon,"ikinci el LG OLED TV",18000,0.18,21240.0,"2025-02-16 07:40:00"
```

girdi veri de (price * (1 + kdv)) değerini hesaplar ve dosyaya yazar. 


## Uygulamanın çalışma adımları

* **1-)** Kafka tek broker olarak ayağa kalkar ve producer containerı kafka topiğine veri girer
* **2-)** Flink Jobmanager ve Taskmanager çalışır iletişimi kurar ve Flink clusterı oluşur
* **3-)** Flink submitter [flink-submit](/Flink_Kafka/flink-submit.py) python scriptini run ile Jobmanager'a iletir ve Job başlatılır.
* **4-)** Python scripti içinde Kafka dan veri okunur, KDV hesaplaması yapılır
* **5-)** TUMBLE windowing (pencereleme) fonksiyonu ile veriler 2 dklık guruplara ayrılır ve veri biriktirilir
* **6-)** write_csv adında tablo oluşturulur ve bu tablo connector: filesystem, format:csv ve path:file:///opt/flink/data yapılandırması yapılır. Tabloya girilen her veri file:///opt/flink/data altındaki dosyaya yazılır.
* **7-)** Ve son olarak bu TUMBLE veriler write_csv tablosuna insert edilir ve lokal dosya sistemine yazılır.

## Mimariyi inceleme ve açıklamalar

### **Network**

```yaml
networks:
  flink-network:
    driver: bridge
```

Yukarıdaki yaml dosyasında okunacağı üzere tüm servislerin sağlıklı çalışabilmesi için flink-network adında bir network tanımlanmıştır.


### **Flink**

```yaml
  jobmanager:
    build: ./PyFlink
    hostname: jobmanager
    container_name: jobmanager
    ports:
      - "8081:8081"
    command: 
      - jobmanager 
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: jobmanager
    networks:
      - flink-network
    restart: on-failure    

  taskmanager:
    build: ./PyFlink
    hostname: taskmanager
    container_name: taskmanager
    depends_on:
      - jobmanager
    command: taskmanager
    scale: 1
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: jobmanager
        taskmanager.numberOfTaskSlots: 16
    volumes:
      - ./out_data/:/opt/flink/data
    networks:
      - flink-network
    read_only: false
    restart: on-failure
```

Yukarıdaki yaml da Jobmanager ve Task manager yapısını görebilirsiniz.

Imajı [PyFlink](/Flink_Kafka/PyFlink/Dockerfile) altındaki Dockerfile ile derler. Imaj içinde Python kurulumu Kafka bağlantısı için jar paketleri ve apache-flink kurulumu yapmaktadır, bu gereklilikler flink jobumuzun sağlıklı çalışmasını sağlamaktadır.

**Jars:**
- [flink-sql-connector-kafka-3.4.0-1.20.jar](https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.4.0-1.20/flink-sql-connector-kafka-3.4.0-1.20.jar)

- [kafka-clients-3.6.1.jar](https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.1/kafka-clients-3.6.1.jar)

- [flink-connector-filesystem_2.12-1.11.6.jar](https://repo1.maven.org/maven2/org/apache/flink/flink-connector-filesystem_2.12/1.11.6/flink-connector-filesystem_2.12-1.11.6.jar)

Jobmanager uı: [http://0.0.0.0:8081](http://0.0.0.0:8081)

![](/readme_images/flink_ui.png)

Jobmanager'a Job gönderme komutu: 

```yaml
flink run -m jobmanager:8081 -py script.py
```

Bu configle 16 task slotu ayarlanmıştır.

```yaml
taskmanager.numberOfTaskSlots: 16 
```

Volume ayarlayarak Job'un çıktılarını lokal dizininizde görmeniz sağlanmıştır. [out_data](/Flink_Kafka/out_data/)


```yaml
volumes:
    - ./out_data/:/opt/flink/data
```

### **Kafka**

```yaml
kafka-flink:
    image: docker.io/bitnami/kafka:3.6
    restart: always
    container_name: kafka-flink
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
      - flink-network
```

Yukarıdaki yaml dosyasından anlaşılacağı üzere 9092 portundan dışarıya bir brokerlı kafka servisi deploy edilmiştir.

Broker adresleri:
- 0.0.0.0:9092
- kafka-flink:9092


### **KafkaUI**

```yaml
kafka-ui-flink:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui-flink
    depends_on:
      - kafka-flink
    ports:
      - 8089:8080
    environment:
      KAFKA_CLUSTERS_0_NAME: kafka
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka-flink:9092
      DYNAMIC_CONFIG_ENABLED: 'true'
    networks:
      - flink-network
    restart: on-failure
```

KafkaUI servisi kafka brokerı olan kafka-flink:9092 ile iletişim kurarak tüm topicleri ve mesajları çeker, bu verileri web üzerinden daha rahat ve kolay görmeye olanak sağlar.

KafkaUI Link: [http://0.0.0.0:8089](http://0.0.0.0:8089)


### **producer**

```yaml
producer:
    container_name: producer
    build: ./producer
    volumes:
      - .:/code
    depends_on:
      - kafka-flink
    networks:
      - flink-network
    restart: on-failure
```

[Producer](/Flink_Kafka/producer/) containerı sayesinde kafka-flink:9092 ye bağlantı kurup sahibinden adında topic oluşturup bu topic içine veri produce ediyoruz.

örnek veriler: [sahibinden-data.json](/Flink_Kafka/producer/sahibinden-data.json)

```json
{"id": 0, "product": "Araba", "description": "ikinci el opel araba", "price": 900000, "kdv": 0.30}
{"id": 1, "product": "Telefon", "description": "sıfır samsung telefon", "price": 50000, "kdv": 0.10}
```


### **flink-submiter**

```yaml
flink-submiter:
    build: ./PyFlink
    container_name: flink-submiter
    environment:
      - |
        FLINK_JOBMANAGER=jobmanager:8081
    command: >
      bash -c "sleep 10 && flink run -m jobmanager:8081 -py /app/flink-submit.py"
    volumes:
      - ./flink-submit.py:/app/flink-submit.py
    networks:
      - flink-network
    restart: on-failure 
```

Bu container içine [flink-submit](/Flink_Kafka/flink-submit.py) script dosyası jobmanager'ın adresi verilerek run edilir. Çalışırken kaynak olarak Flink clusterının kaynaklarını kullanır.

```yaml
command: >
    bash -c "sleep 10 && flink run -m jobmanager:8081 -py /app/flink-submit.py"
```


### **[flink-submit.py](/Flink_Kafka/flink-submit.py)**

Bağımlı olduğu Jar paketlerini dahil etmek.

```python
jars_path = "/opt/flink/lib/"

jar_files = [
    "file:///" + jars_path + "flink-sql-connector-kafka-3.4.0-1.20.jar",
    "file:///" + jars_path + "kafka-clients-3.6.1.jar"
]
jar_files_str = ";".join(jar_files)
```

Bu kod, PyFlink ile bir Stream Execution Environment (çalıştırma ortamı) oluşturur, harici JAR dosyalarını yükler ve SQL işlemleri için bir Table Environment (tablo ortamı) başlatır.

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.add_jars(jar_files_str)

settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(settings)
```

Bu kod, Flink'in Kafka bağlayıcısını kullanarak "sahibinden" adlı bir tablo oluşturur, JSON formatındaki verileri Kafka'dan okur, KDV hesaplaması yapar ve zaman bazlı işlemler için watermark ekler.

```python
topic = "sahibinden"
group = "flink-group-sahibinden"
kafka_bootstrap_server = "kafka-flink:9092"
offset = 'earliest-offset'

table_env.execute_sql("""
    CREATE TABLE sahibinden (
        id INT,
        product STRING,
        description STRING,
        price BIGINT,
        kdv DOUBLE,
        price_with_kdv AS (price * (1 + kdv)),
        timestamp_column TIMESTAMP(3),
        WATERMARK FOR timestamp_column AS timestamp_column - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = '{0}',
        'properties.bootstrap.servers' = '{1}',
        'properties.group.id' = '{2}',
        'scan.startup.mode' = '{3}',
        'value.format' = 'json'
    )
""".format(topic, kafka_bootstrap_server, group, offset))
```

Bu kod, "sahibinden" tablosundaki verileri 2 dakikalık zaman pencereleri (TUMBLE) ile gruplayarak her pencere için id, product, description, price, kdv, price_with_kdv değerlerini döndürür ve pencerenin başlangıç zamanını (window_start) hesaplar.

```python
windowed_table = table_env.sql_query("""
    SELECT 
        id,
        product,
        description,
        price,
        kdv,
        price_with_kdv,
        TUMBLE_START(timestamp_column, INTERVAL '2' MINUTE) AS window_start
    FROM 
        sahibinden
    GROUP BY 
        TUMBLE(timestamp_column, INTERVAL '2' MINUTE), id, product, description, price, kdv, price_with_kdv
""")
```

Bu kod, Flink'in dosya sistemi bağlayıcısını (filesystem) kullanarak verileri CSV formatında /opt/flink/data dizinine yazacak bir "write_csv" tablosu oluşturur ve her satırın virgülle ayrılmasını (csv.field-delimiter = ',') sağlar.

```python
table_env.execute_sql("""
    CREATE TABLE write_csv (
        id INT,
        product STRING,
        description STRING,
        price BIGINT,
        kdv DOUBLE,
        price_with_kdv DOUBLE,
        window_start TIMESTAMP 
    ) WITH (
        'connector' = 'filesystem',
        'format' = 'csv',
        'path' = 'file:///opt/flink/data',
        'csv.field-delimiter' = ',',
        'csv.ignore-parse-errors' = 'true',
        'csv.record-row-delimiter' = '\n'
    )
""")
```

Bu kod, "sahibinden" tablosundaki verileri 2 dakikalık zaman pencereleriyle gruplayarak "write_csv" tablosuna (CSV dosyasına) yazar ve her pencere için window_start zaman damgasını ekler.

```python
table_env.execute_sql("""
    INSERT INTO write_csv
    SELECT 
        id,
        product,
        description,
        price,
        kdv,
        price_with_kdv,
        TUMBLE_START(timestamp_column, INTERVAL '2' MINUTE) AS window_start
    FROM 
        sahibinden
    GROUP BY 
        TUMBLE(timestamp_column, INTERVAL '2' MINUTE), id, product, description, price, kdv, price_with_kdv
""")
```

# **3.b.** 

### **Çok yüklü ama gün içinde dalgalan sıklıkta veri akışı olan bir akışta; zaman ve adet bazlı yazma politikanız nasıl olurdu. Çıkabilkecek ne tür senaryolar olurdu, hangi konfigüsayonlarla yönetirdiniz?**

Spark'ta olduğu gibi, Kubernetes üzerinde bir [Flink](https://artifacthub.io/packages/helm/flink/flink) cluster oluştururdum. JobManager ve TaskManager bileşenlerini, veri boyutuna ve iş yüküne göre optimize ederdim.

Performans odaklı çalışmak için kodları Java ile yazardım. Paralellik seviyesini doğru ayarlayarak işlem verimliliğini artırır, clean code prensiplerine dikkat ederdim.

#### Senaryo ve Çözüm

## Senaryo ve Çözüm

| **Senaryo**             | **Çözüm**                                                        |
|-------------------------|------------------------------------------------------------------|
| Ani veri artışı         | **Dynamic Scaling (autoscale)**: Sistemin otomatik olarak ölçeklenmesini sağlamak ve kaynakları artırmak. **Kafka partitions artırma**: Kafka topic'lerine daha fazla partition ekleyerek veri akışını daha verimli yönetmek. Bu, ani veri artışlarını karşılamak için etkili bir çözüm. |
| Dengesiz veri akışı     | **Adaptive mini-batch (table.exec.mini-batch.size)**: Veriyi küçük mini-batch'lere ayırarak her batch'te belirli bir öğe sayısına ulaşılana kadar işleme işlemini durduruyorum. Bu, kaynak kullanımını optimize eder ve veri akışındaki dengesizlikleri yönetmeye yardımcı olur. |
| Geç gelen veriler       | **Event Time + Watermark stratejisi**: Verilerin doğru sıralamayla işlenmesi için Event Time kullanarak geç gelen verilerin doğru bir şekilde işlenmesini sağlıyorum. Watermark’lar, geç gelen verilerin kaybolmasını engeller ve zaman serisi işlemlerinin tutarlılığını korur. |
| Backpressure            | **Sink paralelliğini artırma**: Backpressure oluştuğunda, sink işlemlerinin paralel çalışmasını artırarak veri yazma hızını optimize ediyorum. Bu, tıkanıklıkların önüne geçer ve verilerin daha hızlı işlenmesini sağlar. |
