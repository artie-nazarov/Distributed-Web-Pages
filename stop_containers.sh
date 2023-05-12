for i in $(seq 1 $1);
do
    docker stop kvs-replica$i
    docker rm kvs-replica$i
done
