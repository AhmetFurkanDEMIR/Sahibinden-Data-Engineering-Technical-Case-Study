FROM flink:latest

RUN apt update

RUN apt install python3 -y

RUN export PATH=$PATH:/usr/local/bin/python3

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get install python3-pip -y

RUN pip3 install apache-flink pyflink

RUN apt-get install nano

RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.4.0-1.20/flink-sql-connector-kafka-3.4.0-1.20.jar -P /opt/flink/lib/

RUN wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.1/kafka-clients-3.6.1.jar -P /opt/flink/lib/

RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-filesystem_2.12/1.11.6/flink-connector-filesystem_2.12-1.11.6.jar -P /opt/flink/lib/

RUN mkdir /opt/flink/data

RUN chmod -R 777 /opt/flink/data