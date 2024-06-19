import socket
import json
import ssl
import threading

# Load hostnames and IP addresses from hosts.json
def load_hosts():
    with open('hosts.json', 'r') as f:
        return json.load(f)

def handle_query(conn, addr, hosts):
    print(f"Connected by {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Received query from {addr[0]}:{addr[1]}")
        query_data = json.loads(data.decode())
        hostname = query_data['hostname']
        if hostname in hosts:
            response = {
                "server_name": "warp-svc",
                "server_address": "127.0.2.2",
                "authority": "Non-authoritative answer",
                "name": hostname,
                "type": "A",
                "addresses": hosts[hostname]
            }
        else:
            response = {
                "server_name": "warp-svc",
                "server_address": "127.0.2.2",
                "authority": "Non-authoritative answer",
                "name": hostname,
                "type": "A",
                "addresses": "Not found"
            }
        response_data = json.dumps(response).encode()
        conn.send(response_data)
    conn.close()

def dns_server(hosts, port=5000):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='server-cert.pem', keyfile='server-key.pem')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', port))
        s.listen()
        print(f"DNS server listening on port {port}...")
        with context.wrap_socket(s, server_side=True) as secure_socket:
            while True:
                conn, addr = secure_socket.accept()
                thread = threading.Thread(target=handle_query, args=(conn, addr, hosts))
                thread.start()

def get_server_settings():
    port = int(input("Enter server port (default is 5000): ") or "5000")
    return port

if __name__ == "__main__":
    hosts = load_hosts()
    port = get_server_settings()
    dns_server(hosts, port)