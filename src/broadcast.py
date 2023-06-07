import concurrent.futures
import requests

def send_request(target, method, data):
    """Sends a `method` request to target, returns -1 if it fails"""
    try:
        if method == "GET":
            return requests.get(target, json=data, timeout=30)
        if method == "PUT":
            return requests.put(target, json=data, timeout=60)
        if method == "DELETE":
            return requests.delete(target, json=data, timeout=10)
    except Exception as e:
        return -1
    
def send_shard_request(path, hosts, method, data):
    """Sends a `method` request to target, returns -1 if it fails"""
    for host in hosts:
        res = None
        target = f"http://{host}/{path}"
        try:
            if method == "GET":
                res = requests.get(target, json=data, timeout=5)
                return res
            if method == "PUT":
                res = requests.put(target, json=data, timeout=5)
                return res
            if method == "DELETE":
                res = requests.delete(target, json=data, timeout=10)
                return res
        except Exception as e:
            pass
    return -1

def broadcast(path, method, data, nodes):
    """Broadcasts a request to every node in the view"""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        rtn = []
        for host in nodes:
            target = f"http://{host}/{path}"
            futures.append(executor.submit(send_request, target=target, method=method, data=data))
        for future in concurrent.futures.as_completed(futures):
            rtn.append(future.result())
    return rtn

def broadcast_shards(path, method, data, nodes):
    """Broadcasts a request to every node in the view"""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        rtn = []
        for hosts, info in zip(nodes, data):
            futures.append(executor.submit(send_shard_request, path=path, hosts=hosts, method=method, data=info))
        for future in concurrent.futures.as_completed(futures):
            rtn.append(future.result())
    return rtn

