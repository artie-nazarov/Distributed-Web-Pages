import Pyro4

class Node2:
    def __init__(self):
        self.name = "Node2"
        self.next_node_uri = None

    def set_next_node(self, next_node_uri):
        self.next_node_uri = next_node_uri

    def get_name(self):
        return self.name

    def send_message(self, message):
        if self.next_node_uri:
            print(f"{self.name} is sending '{message}' to next node")
            next_node = Pyro4.Proxy(self.next_node_uri)
            next_node.send_message(message)
            print(f"{self.name} sent the message '{message}'")
        else:
            print(f"{self.name} received the message '{message}'")

# Start Pyro4 Name Server
ns = Pyro4.locateNS()

# Register Node2 with Pyro4 Name Server
node2 = Node2()
daemon = Pyro4.Daemon()
node2_uri = daemon.register(node2)
ns.register("Node2.node2", node2_uri)

# Wait for Node1 to join the network
print("Waiting for Node1 to join the network...")
while True:
    try:
        node1_uri = ns.lookup("Node1.node1")
        break
    except Pyro4.errors.NamingError:
        pass

# Connect to Node1 and send a message
node2.set_next_node(node1_uri)
node2.send_message("Hello from Node2!")

# Start the Pyro4 event loop
daemon.requestLoop()
