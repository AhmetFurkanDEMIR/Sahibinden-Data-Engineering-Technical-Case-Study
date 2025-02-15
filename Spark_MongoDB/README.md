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