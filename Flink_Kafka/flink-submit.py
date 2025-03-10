# Gerekli PyFlink kütüphaneleri içe aktarılıyor.
from pyflink.table import *
from pyflink.datastream import StreamExecutionEnvironment
import pandas as pd
import time
from pyflink.table.window import Tumble

# Flink'in kullanacağı JAR dosyalarının yolu tanımlanıyor.
jars_path = "/opt/flink/lib/"

# Kafka ve Flink için gerekli olan JAR dosyaları belirleniyor.
jar_files = [
    "file:///" + jars_path + "flink-sql-connector-kafka-3.4.0-1.20.jar",  # Flink'in Kafka ile bağlantı kurmasını sağlayan JAR
    "file:///" + jars_path + "kafka-clients-3.6.1.jar"  # Kafka istemcisi için gerekli JAR dosyası
]

# JAR dosyalarının tek bir string olarak birleştirilmesi (Flink'e yüklenmesi için)
jar_files_str = ";".join(jar_files)

# Flink için akış ortamı oluşturuluyor.
env = StreamExecutionEnvironment.get_execution_environment()
env.add_jars(jar_files_str)  # Belirtilen JAR dosyaları ekleniyor.

# Flink Table API için ortam ayarları oluşturuluyor (Streaming modunda çalıştırılacak).
settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(settings)

topic = "sahibinden" 
group = "flink-group-sahibinden" 
kafka_bootstrap_server = "kafka-flink:9092" 
offset = 'earliest-offset'  # Kafka'daki en eski mesajdan itibaren okumaya başla

# Kafka'dan veri okumak için bir Flink tablosu oluşturuluyor.
table_env.execute_sql("""
    CREATE TABLE sahibinden (
        id INT,  -- Ürün kimliği
        product STRING,  -- Ürün adı
        description STRING,  -- Ürün açıklaması
        price BIGINT,  -- Ürün fiyatı
        kdv DOUBLE,  -- KDV oranı
        price_with_kdv AS (price * (1 + kdv)),  -- KDV dahil fiyat hesaplanıyor (sanal sütun)
        timestamp_column TIMESTAMP(3),  -- Zaman damgası (timestamp)
        WATERMARK FOR timestamp_column AS timestamp_column - INTERVAL '5' SECOND  -- Zaman penceresi belirleme (Geç gelen veriler için 5 saniyelik tolerans)
    ) WITH (
        'connector' = 'kafka',  -- Kafka bağlayıcısı kullanılıyor
        'topic' = '{0}',  -- Kafka konusunun adı
        'properties.bootstrap.servers' = '{1}',  -- Kafka sunucu adresi
        'properties.group.id' = '{2}',  -- Kafka tüketici grubu
        'scan.startup.mode' = '{3}',  -- En eski veriden başlayarak oku
        'value.format' = 'json'  -- Kafka mesajlarının formatı JSON
    )
""".format(topic, kafka_bootstrap_server, group, offset))  # Değişkenler format ile SQL sorgusuna yerleştiriliyor.

# Gruplanmış verileri bir CSV dosyasına yazmak için bir çıktı tablosu oluşturuluyor.
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
        'connector' = 'filesystem',  -- Çıkış bağlayıcısı olarak dosya sistemi kullanılıyor
        'format' = 'csv',  -- Veriler CSV formatında kaydedilecek
        'path' = 'file:///opt/flink/data',  -- Verilerin kaydedileceği dosya yolu
        'csv.field-delimiter' = ',',  -- CSV dosyasında alanları ayırmak için ',' kullanılacak
        'csv.ignore-parse-errors' = 'true',  -- Hatalı satırlar göz ardı edilecek
        'csv.record-row-delimiter' = '\n'  -- Her satır yeni bir satıra yazılacak
    )
""")

# Kafka'dan gelen veriler, belirlenen zaman pencereleri içinde gruplanarak CSV dosyasına yazılıyor.
table_env.execute_sql("""
    INSERT INTO write_csv
    SELECT 
        id,
        product,
        description,
        price,
        kdv,
        price_with_kdv,
        TUMBLE_START(timestamp_column, INTERVAL '2' MINUTE) AS window_start -- 2 dakikalık zaman penceresinin başlangıç zamanı
    FROM 
        sahibinden
    GROUP BY 
        TUMBLE(timestamp_column, INTERVAL '2' MINUTE), id, product, description, price, kdv, price_with_kdv
""")
