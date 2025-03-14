# Sahibinden-Data-Engineering-Technical-Case-Study

### **Proje hakkında**

Bu Proje [Sahibinden.com](https://sahibinden.com/) Data engineer Case çalışmasıdır. Orjinal Case çalışma [dokümanı](/Senior_Data_Enginer_Ankara_Case.doc)

Projedeki açıklamalar ve işlemler README.md dosyasına yazılmıştır. Görüntü ve daha iyi bir gösterim için bu dosyaları Visual Studio Code üzerinden görüntüleyebilirsiniz.

### **Gereklilikler**

![docker](/readme_images/docker.png)

Uygulamaların çalışacağı cihazda docker ve docker compose kurulu olması gerekmektedir. 

[Kurulum linki (Ubuntu için)](https://docs.docker.com/engine/install/ubuntu/)

[Kurulum linki (Windows için)](https://docs.docker.com/desktop/setup/install/windows-install/)


Docker'ı kullanmamın sebebi, Case çalışmasını çalıştıracak kişinin bilgisayarında sorunsuz bir şekilde çalışmasını sağlamaktır. Hem platform bağımsız olarak hatasız çalışmasını sağlamak hem de yazılan uygulamaların daha sonrasında Docker Swarm ve Kubernetes üzerinde deploy edilmesini kolaylaştırmaktır.

Yazılan tüm kodlar ve servisler, otomatik olarak Docker ile deploy edilecek şekilde yapılandırılmıştır. Proje, çalışırken insan faktörünü minimize ederek hata oranını azaltmayı hedeflemektedir.

## 1-) [MySQL ve Debezium](/MySQL_Debezium/)

![1_mimari](/readme_images/1_mimari.png)

[**1.a.**](/MySQL_Debezium/) Localinizde kuracağınız bir mysqli debezium mysql connector ile dinleyip, mysql loglarını kafka topicslerinde gösterecek şekilde bir akış oluşturur musunuz?

[**1.b.**](/MySQL_Debezium/) Buradaki kafka topiclerinde girilen mysql-debezium mesajlarını bir structured DB'ye nasıl upset/merge etmeyi düşünürsünüz, kırılma yaşayacabileceğimiz noktalar nereleri olur, çözüm yaklaşımlarınızı paylaşabilir misiniz? Sözel/text cevap veriniz.


## 2-) [Spark ve MongoDB](/Spark_MongoDB/)

![spark_mongodb_mysql](/readme_images/spark_mongodb_mysql.png)

[**2.a.**](/Spark_MongoDB/) Spark ile mongo dbden veri okuyup yazma:

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

[**2.b.**](/Spark_MongoDB/) Burada 500M'luk bir veri seti olsaydı, bu Spark jobını hangi ortamda nasıl çalıştırırdınız, yaklaşımınız ne olurdu? Sözel/text cevap veriniz.


## 3-) [Flink ve Kafka](/Flink_Kafka/)

![flink_kafka_mimari](/readme_images/flink_kafka_mimari.png)

[**3.a.**](/Flink_Kafka/) Apache Flink ile Kafka entegrasyonu yapıp, Kafka'dan JSON veri okuyup bu veriyi bazı hesaplamalar yaptıktan sonra 2 dakikada bir sonucu  local dosya sistemine csv olarak yazan pipeline oluşturun, örnek implementasyon yapar mısınız?

[**3.b.**](/Flink_Kafka/) Çok yüklü ama gün içinde dalgalan sıklıkta veri akışı olan bir akışta; zaman ve adet bazlı yazma politikanız nasıl olurdu. Çıkabilkecek ne tür senaryolar olurdu, hangi konfigüsayonlarla yönetirdiniz?
