import Pyro4

class Node2:
    def __init__(self):
        # this line sets the name object of the Node2 object to the string Node2
        self.name = "Node2"
        #this line identifies that  there is no next node connected initially
        self.next_node_uri = None
    # this is a method of the node2 class that allows setting the URI of the next node 
    def set_next_node(self, next_node_uri):
        #this line assigns the provided 'next_node_uri' to the 'next_node_uri' attribute of the current Node2 object
        self.next_node_uri = next_node_uri
    # this is a method to retrieve the name of the node
    def get_name(self):
        return self.name
    # this method allows a current node to send a message to the next connected node
    def send_message(self, message):
        # checking there is a next node URI specified 
        if self.next_node_uri:
            # current node sending message to next node
            print(f"{self.name} is sending '{message}' to next node")
            # Creating a procy object 'next node' with the Pyro4 library to represent the remote object located at the URi specified by the next_node_uri
            next_node = Pyro4.Proxy(self.next_node_uri)
            # using send_message method on the next_node object passing the message as an argument 
            next_node.send_message(message)
            #indicating that the message has been sent 
            print(f"{self.name} sent the message '{message}'")
        # executed when there is no next node URI specified
        else:
            #prints a message indicating that the other node has received a message 
            print(f"{self.name} received the message '{message}'")

# uses the 'Pyro4.locateNS() method to locate the Pyro4 Name Server
ns = Pyro4.locateNS()

# creates an instance of the Node2 class named node2
node2 = Node2()
# This line creates a Pyro4 daemon which will be used to register and handle remote objects 
daemon = Pyro4.Daemon()
#registers the node2 object with the Pyro4 Daemon, returning a URI that can be used to access the object remotely 
node2_uri = daemon.register(node2)
# registers the node2 uri with the Pyro4 name server usinh the name Node2.node2
ns.register("Node2.node2", node2_uri)

# Wait for Node1 to join the network
print("Waiting for Node1 to join the network...")
while True:
    try:
        #looks up the URI of node1 from the Pyro4 name server using the name Node1.node1 and assigns it to node1_uri
        node1_uri = ns.lookup("Node1.node1")
        #if the lookup is successful, break out of the loop
        break
    #if the 'NamingError' is raised with the lookup, no action is taken  
    except Pyro4.errors.NamingError:
        pass

# Connect to Node1 and send a message
node2.set_next_node(node1_uri)
node2.send_message("Hello from Node2!")

# Start the Pyro4 event loop, which listens for remote method invocations and handles them. It keeps the program running amd allows remote communication between the two nodes 
daemon.requestLoop()
