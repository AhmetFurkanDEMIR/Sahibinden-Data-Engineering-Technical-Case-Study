#### **1.a.** Localinizde kuracağınız bir mysqli debezium mysql connector ile dinleyip, mysql loglarını kafka topicslerinde gösterecek şekilde bir akış oluşturur musunuz? 

## **Mimari**

![mimari](/readme_images/1_mimari.png)

## Çalışma adımları, inceleme ve açıklamalar

### **Volume ve network**

```yaml
networks:
  bigdata-network:
    driver: bridge

volumes:
  mysql_data:
    driver: local
```

Yukarıdaki yaml dosyasında okunacağı üzere tüm servislerin sağlıklı çalışabilmesi için bigdata-network adında bir network tanımlanmıştır.

mysql servisi içinde mysql_data adında bir volume tanımlanmıştır, böylece mysql servisi restart olsa bile tablolar ve veriler kaybolmayacaktır.

### **MySQL**

```yaml
mysql:
    image: mysql:8.0
    container_name: mysql_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
      MYSQL_USER: debezium
      MYSQL_PASSWORD: debezium
    ports:
      - "3306:3306"
    command: --default-authentication-plugin=mysql_native_password --server-id=1 --log-bin=mysql-bin --binlog-format=ROW --binlog-row-image=FULL
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - bigdata-network
```

Yukarıda mysql servisinin yapılandırmasını görebilirsiniz. Mysql docker imajını kullanarak 3306 portundan servisi ayağa kaldırmaktadır.

```yaml
command: --default-authentication-plugin=mysql_native_password --server-id=1 --log-bin=mysql-bin --binlog-format=ROW --binlog-row-image=FULL
```

Bu command ile mysql de bulunan testdb için CDC aktif hale getirmektedir.

MySQL host: 0.0.0.0:3306

MySQL DB: testdb

MySQL Root user: root
MySQL Root password: root

MySQL user: debezium
MySQL password: debezium