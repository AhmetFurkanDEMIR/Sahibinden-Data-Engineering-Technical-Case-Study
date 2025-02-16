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
