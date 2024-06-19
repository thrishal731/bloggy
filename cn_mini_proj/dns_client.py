import socket
import ssl
import json

def send_dns_query(query, server_address='localhost', port=5000):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations("server-cert.pem")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        with context.wrap_socket(s, server_hostname='thrishal') as secure_socket:
            try:
                secure_socket.connect((server_address, port))
                secure_socket.send(json.dumps(query).encode())
                response_data = secure_socket.recv(1024)
                return json.loads(response_data.decode())
            except Exception as e:
                print(f"Error connecting to the server: {e}")
                return {"error": str(e)}

if __name__ == "__main__":
    hostname = input("Enter hostname: ")
    recursive = input("Perform recursive lookup? (y/n): ").lower() == 'y'
    query = {
        "hostname": hostname,
        "recursive": recursive
    }

    server_address = 'localhost'  
    server_port = 5000  

    response = send_dns_query(query, server_address, server_port)

    # Display output in dig format
    print(f"; <<>> DiG-like output <<>> {query['hostname']}")
    
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(";; global options: +cmd")
        print(";; Got answer:")
        print(f";; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: {response.get('id', 0)}")
        print(";; flags:", "qr rd ra;", f"QUERY: 1, ANSWER: {len(response.get('addresses', []))}, AUTHORITY: 0, ADDITIONAL: 1")
        print("\n;; QUESTION SECTION:")
        print(f";{query['hostname']}.           IN   A\n")
        print(";; ANSWER SECTION:")
        for address in response.get('addresses', []):
            print(f"{query['hostname']}.        {response.get('ttl', 0)}  IN   A   {address}")
        print("\n;; ADDITIONAL SECTION:")
        print(f";; Query time: {response.get('query_time', 0)} msec")
        print(f";; SERVER: {server_address}#{server_port}({server_address})")
        print(f";; WHEN: {response.get('timestamp', 'N/A')}")
        print(f";; MSG SIZE  rcvd: {len(json.dumps(response))}")