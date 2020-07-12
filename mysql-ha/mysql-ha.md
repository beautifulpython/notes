# mysql 高可用
参考文献: https://mysqlhighavailability.com/setting-up-mysql-group-replication-with-mysql-docker-images/

----
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
            - /mnt/db2:/var/lib/mysql
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
            - /mnt/db3:/var/lib/mysql
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
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS                            PORTS                 NAMES
82554e749935        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   6 seconds ago       Up 4 seconds (health: starting)   3306/tcp, 33060/tcp   node3
e48a7a9528ac        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   6 seconds ago       Up 3 seconds (health: starting)   3306/tcp, 33060/tcp   node2
1e1581380ca0        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   6 seconds ago       Up 2 seconds (health: starting)   3306/tcp, 33060/tcp   node1

```

----
在`node1` 上执行以下命令，启动`MySql Group Replication`
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
输出类似如下：
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | 119fd458-c362-11ea-b42d-0242c0a81002 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+

```

在 `node2` 和 `node3`上执行以下命令
```bash
docker exec -it node2 mysql -uroot -pmypass \
  -e "change master to master_user='repl' for channel 'group_replication_recovery';" \
  -e "START GROUP_REPLICATION;"

docker exec -it node3 mysql -uroot -pmypass \
  -e "change master to master_user='repl' for channel 'group_replication_recovery';" \
  -e "START GROUP_REPLICATION;"
```

----

查看集群状态
```bash
docker exec -it node1 mysql -uroot -pmypass \
  -e "SELECT * FROM performance_schema.replication_group_members;"

```
输出结果类似如下:
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | d6b3a7f7-c40a-11ea-af62-0242c0a87002 | node2       |        3306 | ONLINE       |
| group_replication_applier | d769f204-c40a-11ea-af6e-0242c0a87004 | node1       |        3306 | ONLINE       |
| group_replication_applier | d7f40aa2-c40a-11ea-b022-0242c0a87003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+

```

----

创建表格
```bash
docker exec -it node1 mysql -uroot -pmypass \
  -e "create database TEST; use TEST; CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY) ENGINE=InnoDB; show tables;"
```

输出如下：
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+----------------+
| Tables_in_TEST |
+----------------+
| t1             |
+----------------+

```

插入数据
```bash
docker exec -it node2 mysql -uroot -pmypass -e "INSERT INTO TEST.t1 VALUES(2);"
docker exec -it node3 mysql -uroot -pmypass -e "INSERT INTO TEST.t1 VALUES(3);"
```

----

查询插入的数据
```bash
for N in 1 2 3
do docker exec -it node$N mysql -uroot -pmypass \
  -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
  -e "SELECT * FROM TEST.t1;"
done
```
输出类似如下:
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node1 |
+---------------+-------+
+----+
| id |
+----+
|  2 |
|  3 |
+----+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node2 |
+---------------+-------+
+----+
| id |
+----+
|  2 |
|  3 |
+----+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node3 |
+---------------+-------+
+----+
| id |
+----+
|  2 |
|  3 |
+----+

```

----
关闭 `node3`
```bash
$ docker stop node3
$ docker ps
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS                    PORTS                 NAMES
061c976b1d21        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   17 minutes ago      Up 17 minutes (healthy)   3306/tcp, 33060/tcp   node2
7b50362bc008        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   17 minutes ago      Up 17 minutes (healthy)   3306/tcp, 33060/tcp   node1
```

----
查询集群状态
```bash
docker exec -it node1 mysql -uroot -pmypass -e "SELECT * FROM performance_schema.replication_group_members;"
```
输出如下:
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | d6b3a7f7-c40a-11ea-af62-0242c0a87002 | node2       |        3306 | ONLINE       |
| group_replication_applier | d769f204-c40a-11ea-af6e-0242c0a87004 | node1       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+

```

----
在`node3`失效的情况下插入数据
```bash
docker exec -it node1 mysql -uroot -pmypass -e "INSERT INTO TEST.t1 VALUES(1);"
```

查询插入的数据
```bash
docker exec -it node2 mysql -uroot -pmypass \
  -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
  -e "SELECT * FROM TEST.t1;"
```

输出结果如下:
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node2 |
+---------------+-------+
+----+
| id |
+----+
|  1 |
|  2 |
|  3 |
+----+

```

----
恢复 `node3`
```bash
$ docker start node3
$ docker ps
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS                           PORTS                 NAMES
061c976b1d21        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   22 minutes ago      Up 22 minutes (healthy)          3306/tcp, 33060/tcp   node2
ef0eeb740177        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   22 minutes ago      Up 1 second (health: starting)   3306/tcp, 33060/tcp   node3
7b50362bc008        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   22 minutes ago      Up 22 minutes (healthy)          3306/tcp, 33060/tcp   node1

$ docker ps         
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS                    PORTS                 NAMES
061c976b1d21        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   23 minutes ago      Up 23 minutes (healthy)   3306/tcp, 33060/tcp   node2
ef0eeb740177        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   23 minutes ago      Up 33 seconds (healthy)   3306/tcp, 33060/tcp   node3
7b50362bc008        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   23 minutes ago      Up 23 minutes (healthy)   3306/tcp, 33060/tcp   node1

```

----
查询集群状态
```bash
for N in 1 2 3
do
docker exec -it node$N mysql -uroot -pmypass \
    -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
    -e "SELECT * FROM performance_schema.replication_group_members;"
done
```
输出如下，可以看到 `node3` 并不自动加入集群
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node1 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | d6b3a7f7-c40a-11ea-af62-0242c0a87002 | node2       |        3306 | ONLINE       |
| group_replication_applier | d769f204-c40a-11ea-af6e-0242c0a87004 | node1       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node2 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | d6b3a7f7-c40a-11ea-af62-0242c0a87002 | node2       |        3306 | ONLINE       |
| group_replication_applier | d769f204-c40a-11ea-af6e-0242c0a87004 | node1       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node3 |
+---------------+-------+
+---------------------------+-----------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+-----------+-------------+-------------+--------------+
| group_replication_applier |           |             |        NULL | OFFLINE      |
+---------------------------+-----------+-------------+-------------+--------------+
```

----
`node3`重新加入集群
```bash
docker exec -it node3 mysql -uroot -pmypass -e "STOP GROUP_REPLICATION; START GROUP_REPLICATION;"

```

----
查询集群状态
```bash
for N in 1 2 3
do
docker exec -it node$N mysql -uroot -pmypass \
    -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
    -e "SELECT * FROM performance_schema.replication_group_members;"
done
```
输出如下
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node1 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | d6b3a7f7-c40a-11ea-af62-0242c0a87002 | node2       |        3306 | ONLINE       |
| group_replication_applier | d769f204-c40a-11ea-af6e-0242c0a87004 | node1       |        3306 | ONLINE       |
| group_replication_applier | d7f40aa2-c40a-11ea-b022-0242c0a87003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node2 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | d6b3a7f7-c40a-11ea-af62-0242c0a87002 | node2       |        3306 | ONLINE       |
| group_replication_applier | d769f204-c40a-11ea-af6e-0242c0a87004 | node1       |        3306 | ONLINE       |
| group_replication_applier | d7f40aa2-c40a-11ea-b022-0242c0a87003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node3 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | d6b3a7f7-c40a-11ea-af62-0242c0a87002 | node2       |        3306 | ONLINE       |
| group_replication_applier | d769f204-c40a-11ea-af6e-0242c0a87004 | node1       |        3306 | ONLINE       |
| group_replication_applier | d7f40aa2-c40a-11ea-b022-0242c0a87003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+

```

----
查询 `node3` 的数据是否被同步更新
```bash
docker exec -it node3 mysql -uroot -pmypass \
  -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
  -e "SELECT * FROM TEST.t1;"
```
输出如下:
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node3 |
+---------------+-------+
+----+
| id |
+----+
|  1 |
|  2 |
|  3 |
+----+

```

----
关闭`node1`并删除`node1`的数据
```bash
docker stop node1
docker rm node1
sudo rm -rf /mnt/db1
```

----
重启 `docker` 恢复 `node1`
```bash
docker run -d --name=node1 --net=mysql-ha_mysql-group --hostname=node1 \
  -v /mnt/db1:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=mypass \
  mysql/mysql-server:5.7 \
  --server-id=1 \
  --log-bin='mysql-bin-1.log' \
  --enforce-gtid-consistency='ON' \
  --log-slave-updates='ON' \
  --gtid-mode='ON' \
  --transaction-write-set-extraction='XXHASH64' \
  --binlog-checksum='NONE' \
  --master-info-repository='TABLE' \
  --relay-log-info-repository='TABLE' \
  --plugin-load='group_replication.so' \
  --relay-log-recovery='ON' \
  --group-replication-start-on-boot='OFF' \
  --group-replication-group-name='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee' \
  --group-replication-local-address="node1:33061" \
  --group-replication-group-seeds='node1:33061,node2:33061,node3:33061' \
  --loose-group-replication-single-primary-mode='OFF' \
  --loose-group-replication-enforce-update-everywhere-checks='ON'

```

查看`docker` 状态
```bash
$ docker ps
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS                             PORTS                 NAMES
093e0dcc0e4f        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   29 seconds ago      Up 27 seconds (health: starting)   3306/tcp, 33060/tcp   node1
ab4f4e77cd27        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   7 minutes ago       Up 7 minutes (healthy)             3306/tcp, 33060/tcp   node2
3012a6aafa11        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   7 minutes ago       Up 7 minutes (healthy)             3306/tcp, 33060/tcp   node3

$ docker ps
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS                    PORTS                 NAMES
093e0dcc0e4f        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   32 seconds ago      Up 30 seconds (healthy)   3306/tcp, 33060/tcp   node1
ab4f4e77cd27        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   7 minutes ago       Up 7 minutes (healthy)    3306/tcp, 33060/tcp   node2
3012a6aafa11        mysql/mysql-server:5.7   "/entrypoint.sh --se…"   7 minutes ago       Up 7 minutes (healthy)    3306/tcp, 33060/tcp   node3

```

----
查询集群状态
```bash
for N in 1 2 3
do
docker exec -it node$N mysql -uroot -pmypass \
    -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
    -e "SELECT * FROM performance_schema.replication_group_members;"
done
```
输出如下信息
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node1 |
+---------------+-------+
+---------------------------+-----------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+-----------+-------------+-------------+--------------+
| group_replication_applier |           |             |        NULL | OFFLINE      |
+---------------------------+-----------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node2 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | fbdd6128-c444-11ea-a8a2-0242c0a8a002 | node2       |        3306 | ONLINE       |
| group_replication_applier | fd20487f-c444-11ea-a9e1-0242c0a8a003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node3 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | fbdd6128-c444-11ea-a8a2-0242c0a8a002 | node2       |        3306 | ONLINE       |
| group_replication_applier | fd20487f-c444-11ea-a9e1-0242c0a8a003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+

```

----
`node1`重新加入集群
```bash
docker exec -it node1 mysql -uroot -pmypass \
  -e "change master to master_user='repl' for channel 'group_replication_recovery';" \
  -e "START GROUP_REPLICATION;"

```

----

查询集群状态
```bash
for N in 1 2 3
do
docker exec -it node$N mysql -uroot -pmypass \
    -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
    -e "SELECT * FROM performance_schema.replication_group_members;"
done
```

输出如下信息
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node1 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | 9e8df6a8-c448-11ea-88ff-0242c0a8a004 | node1       |        3306 | ONLINE       |
| group_replication_applier | fbdd6128-c444-11ea-a8a2-0242c0a8a002 | node2       |        3306 | ONLINE       |
| group_replication_applier | fd20487f-c444-11ea-a9e1-0242c0a8a003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node2 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | 9e8df6a8-c448-11ea-88ff-0242c0a8a004 | node1       |        3306 | ONLINE       |
| group_replication_applier | fbdd6128-c444-11ea-a8a2-0242c0a8a002 | node2       |        3306 | ONLINE       |
| group_replication_applier | fd20487f-c444-11ea-a9e1-0242c0a8a003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node3 |
+---------------+-------+
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| CHANNEL_NAME              | MEMBER_ID                            | MEMBER_HOST | MEMBER_PORT | MEMBER_STATE |
+---------------------------+--------------------------------------+-------------+-------------+--------------+
| group_replication_applier | 9e8df6a8-c448-11ea-88ff-0242c0a8a004 | node1       |        3306 | ONLINE       |
| group_replication_applier | fbdd6128-c444-11ea-a8a2-0242c0a8a002 | node2       |        3306 | ONLINE       |
| group_replication_applier | fd20487f-c444-11ea-a9e1-0242c0a8a003 | node3       |        3306 | ONLINE       |
+---------------------------+--------------------------------------+-------------+-------------+--------------+

```

----
从`node1`查询数据
```bash
docker exec -it node1 mysql -uroot -pmypass \
  -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
  -e "SELECT * FROM TEST.t1;"
```
输出如下信息
```bash
mysql: [Warning] Using a password on the command line interface can be insecure.
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| hostname      | node1 |
+---------------+-------+
+----+
| id |
+----+
|  1 |
|  2 |
|  3 |
+----+

```

----
关闭集群，并删除数据
```bash
docker stop node1
docker rm node1
docker-compose down
sudo rm -rf /mnt/db1 /mnt/db2 /mnt/db3
```