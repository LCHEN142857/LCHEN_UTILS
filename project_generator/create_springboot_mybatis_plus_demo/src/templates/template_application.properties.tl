server.port=8080

spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.url=jdbc:postgresql://{database_host_port}/{cust_database}
spring.datasource.username={username}
spring.datasource.password={password}

## Mybatis Plus
mybatis-plus.mapper-locations=classpath*:mapping/*.xml
mybatis-plus.type-aliases-package={group_id}.dao.model
mybatis-plus.configuration.log-impl=org.apache.ibatis.logging.stdout.StdOutImpl
mybatis-plus.configuration.cache-enabled=false