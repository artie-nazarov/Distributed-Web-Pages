import concurrent.futures
import requests

def send_request(target, method, data):
    """Sends a `method` request to target, returns -1 if it fails"""
    try:
        if method == "GET":
            return requests.get(target, json=data, timeout=10)
        if method == "PUT":
            return requests.put(target, json=data, timeout=10)
        if method == "DELETE":
            return requests.delete(target, json=data, timeout=10)
    except Exception as e:
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
