from pyflink.table import *
from pyflink.datastream import StreamExecutionEnvironment
import pandas as pd
import time
from pyflink.table.window import Tumble

jars_path = "/opt/flink/lib/"

jar_files = [
    "file:///" + jars_path + "flink-sql-connector-kafka-3.4.0-1.20.jar",
    "file:///" + jars_path + "kafka-clients-3.6.1.jar"
]
jar_files_str = ";".join(jar_files)

env = StreamExecutionEnvironment.get_execution_environment()
env.add_jars(jar_files_str)

settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(settings)

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