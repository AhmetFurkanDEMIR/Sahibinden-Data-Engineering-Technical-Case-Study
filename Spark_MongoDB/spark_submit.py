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


df = spark.read \
    .format("mongodb") \
    .option("uri", "mongodb://mongodb:27017/sahibinden") \
    .option("database", "sahibinden") \
    .option("collection", "collection1") \
    .load()


df.show()

df.printSchema()

df_flat = df.withColumn("c", explode(col("c"))) \
            .withColumn("c_c1", col("c.c1")) \
            .withColumn("c_c2", col("c.c2")) \
            .select("a", "b", "c_c1", "c_c2")

window_spec = Window.partitionBy("a", "b").orderBy("c_c1")


df_flat = df_flat.withColumn("row_num", row_number().over(window_spec)) \
                   .filter(col("row_num") == 1) \
                   .drop("row_num")

df_flat.show()


df_flat.printSchema()


df_flat.write.format("jdbc") \
    .option("url", "jdbc:mysql://mysql_db_spark:3306/testdb?useSSL=false&allowPublicKeyRetrieval=true") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("dbtable", "explode_table") \
    .option("user", "sahibinden") \
    .option("password", "sahibinden") \
    .mode("append") \
    .save()
