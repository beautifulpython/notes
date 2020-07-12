# mysql 高可用
参考文献: https://mysqlhighavailability.com/setting-up-mysql-group-replication-with-mysql-docker-images/

## docker compose
`docker-compose.yml` 内容如下
```yml
version: '3'
services:
    node1:
        image: mysql/mysql-server:5.7
        hostname: node1
        container_name: node1
        networks:
            - mysql-group
        volumes:
            - /mnt/db1:/var/lib/mysql
        environment:
            - MYSQL_ROOT_PASSWORD=mypass
        command: --server-id=1 --log-bin='mysql-bin-1.log' --enforce-gtid-consistency='ON' --log-slave-updates='ON' --gtid-mode='ON' --transaction-write-set-extraction='XXHASH64' --binlog-checksum='NONE' --master-info-repository='TABLE' --relay-log-info-repository='TABLE' --plugin-load='group_replication.so' --relay-log-recovery='ON' --group-replication-start-on-boot='OFF' --group-replication-group-name='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee' --group-replication-local-address="node1:33061" --group-replication-group-seeds='node1:33061,node2:33061,node3:33061' --loose-group-replication-single-primary-mode='OFF' --loose-group-replication-enforce-update-everywhere-checks='ON'
    node2:
        image: mysql/mysql-server:5.7
        hostname: node2
        container_name: node2
        networks:
            - mysql-group
        volumes:
            - /mnt/db1:/var/lib/mysql
        environment:
            - MYSQL_ROOT_PASSWORD=mypass
        command: --server-id=2 --log-bin='mysql-bin-1.log' --enforce-gtid-consistency='ON' --log-slave-updates='ON' --gtid-mode='ON' --transaction-write-set-extraction='XXHASH64' --binlog-checksum='NONE' --master-info-repository='TABLE' --relay-log-info-repository='TABLE' --plugin-load='group_replication.so' --relay-log-recovery='ON' --group-replication-start-on-boot='OFF' --group-replication-group-name='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee' --group-replication-local-address="node2:33061" --group-replication-group-seeds='node1:33061,node2:33061,node3:33061' --loose-group-replication-single-primary-mode='OFF' --loose-group-replication-enforce-update-everywhere-checks='ON'
    node3:
        image: mysql/mysql-server:5.7
        hostname: node3
        container_name: node3
        networks:
            - mysql-group
        volumes:
            - /mnt/db1:/var/lib/mysql
        environment:
            - MYSQL_ROOT_PASSWORD=mypass
        command: --server-id=3 --log-bin='mysql-bin-1.log' --enforce-gtid-consistency='ON' --log-slave-updates='ON' --gtid-mode='ON' --transaction-write-set-extraction='XXHASH64' --binlog-checksum='NONE' --master-info-repository='TABLE' --relay-log-info-repository='TABLE' --plugin-load='group_replication.so' --relay-log-recovery='ON' --group-replication-start-on-boot='OFF' --group-replication-group-name='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee' --group-replication-local-address="node3:33061" --group-replication-group-seeds='node1:33061,node2:33061,node3:33061' --loose-group-replication-single-primary-mode='OFF' --loose-group-replication-enforce-update-everywhere-checks='ON'

networks:
    mysql-group:
```
当前 `mysql`集群包含3个几点，采用多主节点方式启动，启动命令如下:
```bash
docker-compose up -d
```
----
检查启动状况
```bash
$ docker ps
CONTAINER ID        IMAGE                    COMMAND                  CREATED              STATUS                        PORTS                 NAMES
181f9480ed76        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   About a minute ago   Up About a minute (healthy)   3306/tcp, 33060/tcp   mysql-ha_node1_1
1278e1c68f10        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   About a minute ago   Up About a minute (healthy)   3306/tcp, 33060/tcp   mysql-ha_node3_1
fa32a56c4051        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   About a minute ago   Up About a minute (healthy)   3306/tcp, 33060/tcp   mysql-ha_node2_1
```

----
在`node1` 上执行一下命令，启动`MySql Group Replication`
```bash
docker exec -it node1 mysql -uroot -pmypass \
  -e "SET @@GLOBAL.group_replication_bootstrap_group=1;" \
  -e "create user 'repl'@'%';" \
  -e "GRANT REPLICATION SLAVE ON *.* TO repl@'%';" \
  -e "flush privileges;" \
  -e "change master to master_user='repl' for channel 'group_replication_recovery';" \
  -e "START GROUP_REPLICATION;" \
  -e "SET @@GLOBAL.group_replication_bootstrap_group=0;" \
  -e "SELECT * FROM performance_schema.replication_group_members;"
```
