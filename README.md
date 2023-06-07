# Decentralized-Internet
Decentralized Internet - CSE 115 Project

## About

A decentralized document sharing system for delivering files and SPA's over a network. 
Runs on top of a distributed, fault-tolerant, highly available KVS

## Installation

First clone the git repository
`git clone https://github.com/artie-nazarov/Decentralized-Internet.git`

If running in a local docker cluster, initialize a network with
`docker network create --subnet=[INSERT IP RANGE] dci_subnet`

Then build the docker image
`docker build -t decentralized_net:1.0 .`

Finally, run the docker image
`docker run -p 8080:8080 --env ADDRESS="[INSERT_IP]:8080" decentralized_net:1.0`

Or if using a docker network 
`docker run -p 8080:8080 --net dci_subnet --env ADDRESS="[INSERT_IP]:8080" decentralized_net:1.0`

Alternatively, we include `start_containers.sh` and `stop_containers.sh` as automated ways to launch a collection of docker images at once, which assumes you've allocated the IPs 10.10.0.0/16 to the docker network
`./start_containers.sh [NUM]`

## Usage 

To access the UI for the network, open a web browser and navigate to the ip assigned to the running instance of the server. If you're using the `start_nodes.sh` script, it will be at 10.10.0.1
Initialize the network by giving it the list of all nodes you want to add, and from there you're free to start sharing files!


