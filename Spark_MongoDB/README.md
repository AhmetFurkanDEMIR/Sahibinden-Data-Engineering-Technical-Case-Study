# **2.a.** 
### **Spark ile mongodb den veri okuyup yazma**
```sql
CREATE TABLE collection1 (
   a bigint,
   b bigint,
   c array(ROW(c1 varchar, c2 bigint))
);
```

formatında bir collectiondan 1 satır veri okuyup (c kolonunda 3 rows item olduğunu düşünelim), structured bir dbye 

```sql
CREATE TABLE sql_table(
   a int, 
   b int, 
   c_c1 varchar, 
   c_c2 int
); 
```

şeklinde bir tabloya 3 satır olarak insert edebilir misiniz?

## **Mimari**

![spark_mongodb_mysql](/readme_images/spark_mongodb_mysql.png)


## Uygulamayı çalıştırma

Spark_MongoDB projesine ilerleyin

```yaml
cd Spark_MongoDB
```

docker compose up komutunu terminalde çalıştırın ve projenin ayağa kalmasını bekleyin (15 Sn)

![mysql_mongo_spark_run](/readme_images/mysql_mongo_spark_run.png)

Eğer ilk kez çalıştırıyorsanız, Docker Hub üzerinden ihtiyaç duyulan imajlar bir defaya mahsus lokal bilgisayarınıza çekilecektir.

[MySQL DockerHub](https://hub.docker.com/_/mysql)

[Apache Spark DockerHub](https://hub.docker.com/_/spark)

[MongoDB DockerHub](https://hub.docker.com/_/mongo)

Docker imajları otomatik olarak ayağa kalkıp işlemleri başlatacaktır.

Spark clusterını incelemek için master url: [http://0.0.0.0:8080/](http://0.0.0.0:8080/)

![spark_master](/readme_images/spark_master.png)

Spark deploy edildikten sonra MongoDB deploy edilmektedir. MongoDB deploy edilirken [init.js](/Spark_MongoDB/init.js) dosyası ile veri oluşturulmaktadır.

MongoDB connection string: mongodb://0.0.0.0:27017/

![mongo_compas](/readme_images/mongo_compas.png)

Ardından MySQL deploy edilmektedir ve deploy sırasında [init.sql](/Spark_MongoDB/init.sql) kullanılarak aşağıdaki tablo otomatik olarak oluşturulur.

```sql
CREATE TABLE IF NOT EXISTS explode_table (
    a INT,
    b INT,
    c_c1 VARCHAR(255),
    c_c2 INT
);
```

Son aşama olarak spark-submiter ile [spark_submit.py](/Spark_MongoDB/spark_submit.py) dosyası Spark clusterına submit edilir. Spark, MongoDB deki verileri okuyup işlemleri tamamlandıktan sonra MySQL de ki testdb.explode_table'a yazma işlemini yapar.

![explode_table](/readme_images/explode_table.png)
(MongoDB deki veriyi istenilen formata uygun olarak MySQL'e yazmak)

## Uygulamanın çalışma adımları

* **1-)** MySQL servisinin deploy edilmesi ve tablonun oluşturulması
* **2-)** MongoDB'nin deploy edilmesi ve verilerin insert edilmesi
* **3-)** 1 master ve 2 worker Spark clusterının deploy edilmesi
* **4-)** Spark-submiter ile [spark_submit](/Spark_MongoDB/spark_submit.py) scriptinin client modunda submit edilmesi
* **5-)** spark_submit.py içindeki işlemler ile MongoDB verilerini explode edip MySQL deki tabloya verilerin yazılması

## Mimariyi inceleme ve açıklamalar

### **Volume ve network**

```yaml
networks:
  spark-network:
    driver: bridge

volumes:
  mongo_data:
    driver: local

  mysql_data_spark:
    driver: local
```

Yukarıdaki yaml dosyasında okunacağı üzere tüm servislerin sağlıklı çalışabilmesi için spark-network adında bir network tanımlanmıştır.

mysql servisi içinde mysql_data_spark adında bir volume tanımlanmıştır, böylece mysql servisi restart olsa bile tablolar ve veriler kaybolmayacaktır. Aynı işlem mongo_data adındaki volume ile MongoDB'ye de sağlanmıştır.

### **MySQL**

```yaml
mysql_db_spark:
    image: mysql:8.0
    container_name: mysql_db_spark
    restart: always
    command: --default-authentication-plugin=mysql_native_password --server-id=1 --log-bin=mysql-bin --binlog-format=ROW --binlog-row-image=FULL
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
      MYSQL_USER: sahibinden
      MYSQL_PASSWORD: sahibinden
    ports:
      - "3306:3306"
    volumes:
      - mysql_data_spark:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - spark-network
```

Yukarıda mysql servisinin yapılandırmasını görebilirsiniz. Mysql docker imajını kullanarak 3306 portundan servisi ayağa kaldırmaktadır.

[init.sql](/Spark_MongoDB/init.sql) dosyası ile otomatik olarak tablo oluşturulur.

- MySQL host: 0.0.0.0:3306
- MySQL DB: testdb
- MySQL Root user: root
- MySQL Root password: root
- MySQL user: sahibinden
- MySQL password: sahibinden

### **MongoDB**

```yaml
mongodb:
    image: mongo:latest
    container_name: mongodb
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
      - ./init.js:/docker-entrypoint-initdb.d/init.js:ro
    environment:
      MONGO_INITDB_DATABASE: sahibinden
    networks:
      - spark-network
```

27017 portundan dışarıyla iletişim kurabilecek şekilde MongoDB servisinin deploy edilmesi.

```yaml

    volumes:
      - mongo_data:/data/db
      - ./init.js:/docker-entrypoint-initdb.d/init.js:ro
```

[init.js](/Spark_MongoDB/init.js) dosyası ile veriler MongoDB ye insert edilir. 


### **Spark Cluster**

```yaml
spark-master:
    image: bitnami/spark:latest
    container_name: spark-master
    hostname: spark-master
    environment:
      - SPARK_MODE=master
      - SPARK_DAEMON_MEMORY=16g
      - SPARK_WORKER_INSTANCES=2
      - SPARK_EXECUTOR_MEMORY=16g
      - SPARK_WORKER_CORES=8
    ports:
      - "8080:8080"  # Web UI için
      - "7077:7077"  # Master URL
    deploy:
      resources:
        limits:
          cpus: "8"  # Increase the number of CPUs
          memory: "16G"  # Increase the amount of memory
    restart: on-failure
    networks:
      - spark-network

  spark-worker-1:
    image: bitnami/spark:latest
    container_name: spark-worker-1
    hostname:  spark-worker-1
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=8g
      - SPARK_EXECUTOR_MEMORY=8g
    depends_on:
      - spark-master
    deploy:
      resources:
        limits:
          cpus: "8"  # Increase the number of CPUs
          memory: "16G"  # Increase the amount of memory
    restart: on-failure
    networks:
      - spark-network

  spark-worker-2:
    image: bitnami/spark:latest
    container_name: spark-worker-2
    hostname:  spark-worker-2
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=8g
      - SPARK_EXECUTOR_MEMORY=8g
    depends_on:
      - spark-master
    deploy:
      resources:
        limits:
          cpus: "8"  # Increase the number of CPUs
          memory: "16G"  # Increase the amount of memory
    restart: on-failure
    networks:
      - spark-network
```

1 master 2 worker olacak şekilde Spark clusterı deploy edilir.

```yaml
resources:
    limits:
        cpus: "8"  # Increase the number of CPUs
        emory: "16G"  # Increase the amount of memory

```

Her worker için 8 CPU ve 16GB memory ayarlanmıştır.

- Spark master web url: [http://0.0.0.0:8080/](http://0.0.0.0:8080/)
- Spark master url: spark://spark-master:7077

### **Spark Submiter**

```yaml
spark-submiter:
    image: bitnami/spark:latest
    container_name: spark-submiter
    depends_on:
      - mysql_db_spark
      - spark-master
      - mongodb
    command: >
      bash -c "sleep 15 && spark-submit --master spark://spark-master:7077 --packages org.mongodb.spark:mongo-spark-connector_2.12:10.4.1,mysql:mysql-connector-java:8.0.33 --conf spark.mongodb.read.connection.uri=mongodb://mongodb:27017/sahibinden --conf spark.mongodb.write.connection.uri=mongodb://mongodb:27017/sahibinden --conf spark.cores.max=2 --conf spark.driver.memory=4g /opt/spark_scripts/spark_submit.py"
    volumes:
      - ./spark_submit.py:/opt/spark_scripts/spark_submit.py
    networks:
      - spark-network
```

[spark_submit.py](/Spark_MongoDB/spark_submit.py) dosyasını Spark clusterına submit eden container.

```yaml
spark-submit --master spark://spark-master:7077 --packages org.mongodb.spark:mongo-spark-connector_2.12:10.4.1,mysql:mysql-connector-java:8.0.33 --conf spark.mongodb.read.connection.uri=mongodb://mongodb:27017/sahibinden --conf spark.mongodb.write.connection.uri=mongodb://mongodb:27017/sahibinden --conf spark.cores.max=2 --conf spark.driver.memory=4g /opt/spark_scripts/spark_submit.py
```

spark-submit komutu

### **[spark_submit.py](/Spark_MongoDB/spark_submit.py)**

Bu Python scripti içerisinde MongoDB den veriler okunup explode edilip ardından MySQL'e yazma işlemini yapar.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, row_number
from pyspark import SparkContext,SparkConf
from pyspark.sql.window import Window

conf = SparkConf().set("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.4.1")
sc = SparkContext(conf=conf)

# Spark Session oluşturma
spark = SparkSession.builder \
    .appName("MongoDB to SQL") \
    .master("spark://spark-master:7077") \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:10.4.1,mysql:mysql-connector-java:8.0.33')\
    .config("spark.mongodb.read.connection.uri", "mongodb://mongodb:27017/sahibinden.collection1") \
    .config("spark.mongodb.write.connection.uri", "mongodb://mongodb:27017/sahibinden.collection1") \
    .config("spark.driver.memory", "4g") \
    .config("spark.cores.max", 2) \
    .getOrCreate()

# verileri MongoDB den okuma
df = spark.read \
    .format("mongodb") \
    .option("uri", "mongodb://mongodb:27017/sahibinden") \
    .option("database", "sahibinden") \
    .option("collection", "collection1") \
    .load()


df.show()

df.printSchema()

# explode işlemi, c satırındaki verileri c_1 ve c_2 olarak ekleme
df_flat = df.withColumn("c", explode(col("c"))) \
            .withColumn("c_c1", col("c.c1")) \
            .withColumn("c_c2", col("c.c2")) \
            .select("a", "b", "c_c1", "c_c2")
df_flat.show()
df_flat.printSchema()

# mysql'e yazma
df_flat.write.format("jdbc") \
    .option("url", "jdbc:mysql://mysql_db_spark:3306/testdb?useSSL=false&allowPublicKeyRetrieval=true") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("dbtable", "explode_table") \
    .option("user", "sahibinden") \
    .option("password", "sahibinden") \
    .mode("append") \
    .save()
```