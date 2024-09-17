# Distributed Web Pages
## Idea
This project aims to explore the idea of creating a version of Decentralized Internet. The goal is to give users a platform to store their Web Pages (or any file for that matter!) within a decentralized network of trusted peers. Once a user joins such a network of peers they can access or add custom Web Pages and contribute to the growth of this decentralized subset of the internet. 
## Web Browser
The user-facing application is the Browser which allows
* Creating/Joining other people's networks
* Lookup Web Pages (files) on the network and viewing them.
## Distributed Storage
The technology behind our distributed file storage system is an **eventually consistent**, **durable**, **replicated**, **sharded** key-value store.
### The Peer Network
Each node has a **consistent** view of the network - the view is updated across all nodes in the network.
Note: This approach is a known availability bottle-neck and was chosen for simplicity.
### Eventually consistent KV Store
Our distributed KV store maintains events state via [Vector Clocks](https://en.wikipedia.org/wiki/Vector_clock) and enables highly available non-hanging writes (single round-trip per shard latency), and eventually consistent reads.
### Durability
Our system ensures all writes are persisted to disk before an ack response is returned to the client
### Sharding
This feature provides the **distribution** of the data on the network. Upon network creation we assign all peer nodes to shards, balancing both data sharding as well as replication per shard. When a user of the network attempts to Read or Write data, a request will be issued to each shard, and within each shard one of the available replicas will process the request and for writes will broadcast new data to the other replicas.
## Usage
### Test locally
Prerequisites: Docker
```start_containers.sh <number_of_nodes>```
### Test across multiple machines
If you want to test the functionality across multiple computers, they all need to be connected to the same local network.
Run ```python src/app.py``` to start a Flask server on each machine
<br>
**After setting up the servers open up the Browser, create your network by addding ip addresses of all the peers, add your Web Pages to the network or view other people's shared files!**
