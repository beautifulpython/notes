## Dockerfile.1604 usage

### build docker
```bash
docker build -t cmp:1604 -f Dockerfile.1604 ./
```

### list image
```bash
docker image list
```

### list container
```bash
docker ps -a
```

### remove container
```bash
docker rm <container-id>
```

### remove image
```bash
docker rmi <image -id>
```

### start docker
```bash
docker run -ti cmp:1604 bash
```

### source conda env
```bash
. /opt/conda/etc/profile.d/conda.sh
```

### create conda env and install gdal=3.0.4
```bash
conda create -n gdal-dev -c conda-forge gdal=3.0.4
```
