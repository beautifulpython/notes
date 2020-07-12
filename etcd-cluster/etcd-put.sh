
export ETCDCTL_API=3
HOST_1=172.20.0.101
HOST_2=172.20.0.102
HOST_3=172.20.0.103
ENDPOINTS=$HOST_1:2379,$HOST_2:2379,$HOST_3:2379

etcdctl --endpoints=$ENDPOINTS member list
etcdctl --endpoints=$ENDPOINTS put foo "hello world"
etcdctl --endpoints=$ENDPOINTS get foo
