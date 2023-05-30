docker build -t kvs:1.0 .

for i in $(seq 1 $1);
do
    docker run -d --net kv_subnet --ip 10.10.0.$(($i+1)) --name "kvs-replica$i" -v $(pwd)/src/:/src --publish 808$(($i-1)):8080 --env ADDRESS="10.10.0.$(($i+1)):8080" kvs:1.0
done
for i in $(seq 1 $1);
do
    echo -n "808$(($i-1)):10.10.0.$(($i+1)):8080 "
done
