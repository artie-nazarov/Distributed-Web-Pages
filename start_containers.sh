docker build -t decentralized_net:1.0 .

for i in $(seq 1 $1);
do
    docker run -d --net dci_subnet --ip 10.10.0.$(($i+1)) --name "dci_node$i" -v $(pwd)/src/:/src --publish 808$(($i-1)):8080 --env ADDRESS="10.10.0.$(($i+1)):8080" decentralized_net:1.0
done
