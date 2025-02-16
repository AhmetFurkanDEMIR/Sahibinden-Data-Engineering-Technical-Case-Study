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

İlk olarak Kafka tek broker olarak ayağa kalkar ver ![](/Flink_Kafka/producer/kafka_producer.py) python scripti ile kafkaya veri yazar.

[KafkaUI](http://0.0.0.0:8089/ui/clusters/kafka/all-topics?perPage=25)

![](/readme_images/flink_kafka_ui.png)

Ardından Flink jobmanager ve taskmanager ayağa kalkar birbirleriyle iletişim kurar ve cluster oluşturur.

![flink_ui](/readme_images/flink_ui.png)

Son olarak Flink Submitter adlı container [flink-submit.py](/Flink_Kafka/flink-submit.py) python scriptini run komutu ile jobmanager'a iletir ve job'u başlatır.

![flink_running_job](/readme_images/flink_running_job.png)

Yukarıdaki resimde görüleceği üzere Job'un başladığını ve running durumunda olduğunu görebilirsiniz.