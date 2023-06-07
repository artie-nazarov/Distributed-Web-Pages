for i in $(seq 1 $1);
do
    docker stop dci_node$i
    docker rm dci_node$i
done
