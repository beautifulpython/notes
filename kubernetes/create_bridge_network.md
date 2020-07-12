# Create bridge network device

参考: https://cloud.tencent.com/developer/article/1610117

接下来，使用以下nmcli命令创建一个网桥接口，其中conn或con代表连接，连接名称为br0，接口名称也为br0。
```bash
nmcli conn add type bridge con-name br0 ifname br0
```

在桥接模式下，虚拟机很容易访问物理网络，它们与主机位于同一子网中，并且可以访问DHCP等服务。要设置静态IP地址，请运行以下命令来设置br0连接的IPv4地址、网络掩码、默认网关和DNS服务器（根据您的环境设置值)
```bash
nmcli conn modify br0 ipv4.addresses '192.168.1.1/24'
nmcli conn modify br0 ipv4.gateway '192.168.1.1'
nmcli conn modify br0 ipv4.dns '192.168.1.1'
nmcli conn modify br0 ipv4.method manual
```

现在，如图所示，将以太网接口（enp2s0）作为便携式设备添加到网桥（br0）连接中
```bash
nmcli conn add type ethernet slave-type bridge con-name bridge-br0 ifname enp2s0 master br0
```

接下来，打开或激活网桥连接，您可以使用如下所示的连接名称或UUID
```bash
nmcli conn up br0
```

接下来，使用以下bridge命令显示当前桥端口配置和标志
```bash
bridge link show
```

或者使用brctl命令查看
```bash
 brctl show
```