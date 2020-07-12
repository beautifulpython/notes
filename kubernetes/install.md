# 安装 Kubernetes

## 系统信息
使用 `VirtualBox` 创建 `kubernets` 集群，系统配置信息如下。
vbox name | host name | ip | cpu cores | memory | user name | passwd
---|---|---|---|---|---|---
kmaster | master | 192.168.1.220 | 4 | 8G | master  | k8s
knode1  | node1  | 192.168.1.221 | 2 | 8G | master  | k8s
knode2  | node2  | 192.168.1.222 | 2 | 8G | master  | k8s

操作系统: `Ubuntu 18.04.4 64位`

## 配置一台`vbox`虚拟机

### 配置`aliyun`的源
```bash
sudo vim /etc/apt/sources.list
```
```vim
:%s/cn.archive.ubuntu.com/mirrors.aliyun.com/g
```

### 安装 `openssh-server`
```bash
sudo apt-get update
sudo apt-get install openssh-server
```

### 关闭 `swap`
```bash
$ sudo swapoff -a
$ free -h
              total        used        free      shared  buff/cache   available
Mem:           7.8G        146M        7.1G        996K        593M        7.4G
Swap:            0B          0B          0B
```
编辑 `/etc/fstab` 注释掉 `swap`
```txt
/dev/disk/by-uuid/62c51279-a79c-4e9d-8432-a1a59f4cdba0 / ext4 defaults 0 0
#/swap.img      none    swap    sw      0       0
```

### 编辑 `hosts`
在 `/etc/hosts` 添加
```txt
192.168.1.220 master
192.168.1.221 node1 
192.168.1.222 node2
```

### 安装 `docker`
参考： https://docs.docker.com/engine/install/ubuntu/
```bash
sudo apt-get install \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg-agent \
     software-properties-common
```

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

```bash
sudo add-apt-repository \
     "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) \
     stable"
```

```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

### 配置 `docker` 镜像代理
参考: https://docs.docker.com/config/daemon/systemd/
```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
```
编辑文件 `/etc/systemd/system/docker.service.d/http-proxy.conf`
```conf
[Service]
Environment="HTTP_PROXY=http://192.168.1.32:8123"
Environment="HTTPS_PROXY=http://192.168.1.32:8123"
Environment="NO_PROXY=localhost,127.0.0.1"
```
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```
检查代理是否设置
```bash
$ sudo systemctl show --property=Environment docker
Environment=HTTP_PROXY=http://192.168.1.32:8123 HTTPS_PROXY=http://192.168.1.32:8123 NO_PROXY=localhost,127.0.0.1
```
验证代理能否通过代理下载
```bash
$ sudo docker pull httpd
Using default tag: latest
latest: Pulling from library/httpd
8559a31e96f4: Pull complete 
bd517d441028: Pull complete 
f67007e59c3c: Pull complete 
83c578481926: Pull complete 
f3cbcb88690d: Pull complete 
Digest: sha256:387f896f9b6867c7fa543f7d1a686b0ebe777ed13f6f11efc8b94bec743a1e51
Status: Downloaded newer image for httpd:latest
docker.io/library/httpd:latest
```

### 设置 `kubernetes` 阿里云镜像
参考: https://developer.aliyun.com/mirror/kubernetes
```bash
curl https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg | sudo apt-key add - 
```
编辑 `/etc/apt/sources.list.d/kubernetes.list`
```conf
deb https://mirrors.aliyun.com/kubernetes/apt/ kubernetes-xenial main
```
```
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
```

## 复制 `vbox` 虚拟机器
关闭当前虚拟机器，并复制生成 `node1`， `node2`，需要修改虚拟机的 `hostname` 和 `ip address`

## 后台启动 `vbox` 
```
$ vboxmanage startvm kmaster --type headless
Waiting for VM "kmaster" to power on...
VM "kmaster" has been successfully started.
$ vboxmanage startvm knode1 --type headless
Waiting for VM "knode1" to power on...
VM "knode1" has been successfully started.
$ vboxmanage startvm knode2 --type headless
Waiting for VM "knode2" to power on...
VM "knode2" has been successfully started.
```

## 设置 `kubernetes` 集群

### `master` 节点设置

`kubernetes` 集群初始化
```bash
$ sudo kubeadm init --apiserver-advertise-address 192.168.1.220 --pod-network-cidr=172.16.0.0/16
W0705 10:28:07.286983    1853 configset.go:202] WARNING: kubeadm cannot validate component configs for API groups [kubelet.config.k8s.io kubeproxy.config.k8s.io]
[init] Using Kubernetes version: v1.18.5
[preflight] Running pre-flight checks
	[WARNING IsDockerSystemdCheck]: detected "cgroupfs" as the Docker cgroup driver. The recommended driver is "systemd". Please follow the guide at https://kubernetes.io/docs/setup/cri/
[preflight] Pulling images required for setting up a Kubernetes cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection
[preflight] You can also perform this action in beforehand using 'kubeadm config images pull'
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Starting the kubelet
[certs] Using certificateDir folder "/etc/kubernetes/pki"
[certs] Generating "ca" certificate and key
[certs] Generating "apiserver" certificate and key
[certs] apiserver serving cert is signed for DNS names [master kubernetes kubernetes.default kubernetes.default.svc kubernetes.default.svc.cluster.local] and IPs [10.96.0.1 192.168.1.220]
[certs] Generating "apiserver-kubelet-client" certificate and key
[certs] Generating "front-proxy-ca" certificate and key
[certs] Generating "front-proxy-client" certificate and key
[certs] Generating "etcd/ca" certificate and key
[certs] Generating "etcd/server" certificate and key
[certs] etcd/server serving cert is signed for DNS names [master localhost] and IPs [192.168.1.220 127.0.0.1 ::1]
[certs] Generating "etcd/peer" certificate and key
[certs] etcd/peer serving cert is signed for DNS names [master localhost] and IPs [192.168.1.220 127.0.0.1 ::1]
[certs] Generating "etcd/healthcheck-client" certificate and key
[certs] Generating "apiserver-etcd-client" certificate and key
[certs] Generating "sa" key and public key
[kubeconfig] Using kubeconfig folder "/etc/kubernetes"
[kubeconfig] Writing "admin.conf" kubeconfig file
[kubeconfig] Writing "kubelet.conf" kubeconfig file
[kubeconfig] Writing "controller-manager.conf" kubeconfig file
[kubeconfig] Writing "scheduler.conf" kubeconfig file
[control-plane] Using manifest folder "/etc/kubernetes/manifests"
[control-plane] Creating static Pod manifest for "kube-apiserver"
[control-plane] Creating static Pod manifest for "kube-controller-manager"
W0705 10:30:31.594348    1853 manifests.go:225] the default kube-apiserver authorization-mode is "Node,RBAC"; using "Node,RBAC"
[control-plane] Creating static Pod manifest for "kube-scheduler"
W0705 10:30:31.595219    1853 manifests.go:225] the default kube-apiserver authorization-mode is "Node,RBAC"; using "Node,RBAC"
[etcd] Creating static Pod manifest for local etcd in "/etc/kubernetes/manifests"
[wait-control-plane] Waiting for the kubelet to boot up the control plane as static Pods from directory "/etc/kubernetes/manifests". This can take up to 4m0s
[apiclient] All control plane components are healthy after 26.002527 seconds
[upload-config] Storing the configuration used in ConfigMap "kubeadm-config" in the "kube-system" Namespace
[kubelet] Creating a ConfigMap "kubelet-config-1.18" in namespace kube-system with the configuration for the kubelets in the cluster
[upload-certs] Skipping phase. Please see --upload-certs
[mark-control-plane] Marking the node master as control-plane by adding the label "node-role.kubernetes.io/master=''"
[mark-control-plane] Marking the node master as control-plane by adding the taints [node-role.kubernetes.io/master:NoSchedule]
[bootstrap-token] Using token: otclmk.joyxinbfqjrcbadf
[bootstrap-token] Configuring bootstrap tokens, cluster-info ConfigMap, RBAC Roles
[bootstrap-token] configured RBAC rules to allow Node Bootstrap tokens to get nodes
[bootstrap-token] configured RBAC rules to allow Node Bootstrap tokens to post CSRs in order for nodes to get long term certificate credentials
[bootstrap-token] configured RBAC rules to allow the csrapprover controller automatically approve CSRs from a Node Bootstrap Token
[bootstrap-token] configured RBAC rules to allow certificate rotation for all node client certificates in the cluster
[bootstrap-token] Creating the "cluster-info" ConfigMap in the "kube-public" namespace
[kubelet-finalize] Updating "/etc/kubernetes/kubelet.conf" to point to a rotatable kubelet client certificate and key
[addons] Applied essential addon: CoreDNS
[addons] Applied essential addon: kube-proxy

Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.1.220:6443 --token otclmk.joyxinbfqjrcbadf \
    --discovery-token-ca-cert-hash sha256:fd6f00236aad2f7886ef88268cb8cf1d834b7ebadfe6a195af1c44fffab0a446 
```

设置 `kubernetes` 配置文件

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

设置 `kubernetes` 网络配置文件


```bash
$ wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
$ sudo kubectl apply -f kube-flannel.yml
podsecuritypolicy.policy/psp.flannel.unprivileged created
clusterrole.rbac.authorization.k8s.io/flannel created
clusterrolebinding.rbac.authorization.k8s.io/flannel created
serviceaccount/flannel created
configmap/kube-flannel-cfg created
daemonset.apps/kube-flannel-ds-amd64 created
daemonset.apps/kube-flannel-ds-arm64 created
daemonset.apps/kube-flannel-ds-arm created
daemonset.apps/kube-flannel-ds-ppc64le created
daemonset.apps/kube-flannel-ds-s390x created
```

查看`master`节点配置

```bash
$ kubectl get nodes
NAME     STATUS     ROLES    AGE     VERSION
master   NotReady   master   3m12s   v1.18.5

$ kubectl get nodes
NAME     STATUS   ROLES    AGE     VERSION
master   Ready    master   3m17s   v1.18.5
```

### 设置 `node1`、`node2`

加入`kubernetes`集群

```bash
sudo kubeadm join 192.168.1.220:6443 --token otclmk.joyxinbfqjrcbadf \
    --discovery-token-ca-cert-hash sha256:fd6f00236aad2f7886ef88268cb8cf1d834b7ebadfe6a195af1c44fffab0a446
```

查看`kubernetes`节点配置

```
$ kubectl get nodes
NAME     STATUS     ROLES    AGE     VERSION
master   Ready      master   6m51s   v1.18.5
node1    NotReady   <none>   73s     v1.18.5
node2    NotReady   <none>   29s     v1.18.5

$ kubectl get nodes
NAME     STATUS   ROLES    AGE     VERSION
master   Ready    master   7m26s   v1.18.5
node1    Ready    <none>   108s    v1.18.5
node2    Ready    <none>   64s     v1.18.5

```

## 启动 `httpd`
在`master`节点上执行
```bash
kubectl run my-httpd --image=httpd --port=80
```

验证是否执行
```bash
$ kubectl get pod -o wide
NAME       READY   STATUS    RESTARTS   AGE   IP           NODE    NOMINATED NODE   READINESS GATES
my-httpd   1/1     Running   0          82s   172.16.1.2   node1   <none>           <none>
```
