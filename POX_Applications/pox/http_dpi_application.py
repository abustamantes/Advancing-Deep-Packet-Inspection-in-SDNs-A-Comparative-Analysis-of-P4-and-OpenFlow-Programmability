def process_http(tcp_segment, blacklist_hosts):
    try:
        http_payload = tcp_segment.payload.decode('utf-8')  # Decode payload to string
        print(f"http_payload: {http_payload}")

        # Check if it's a GET request and extract the host
        if "GET " in http_payload:
            # Extracting the host from the HTTP header
            host_start = http_payload.find("Host: ") + 6
            host_end = http_payload.find("\r\n", host_start)
            host = http_payload[host_start:host_end].strip()

            # Check if the host is in the blacklist set
            if host in blacklist_hosts:
                print("Dropping packet due to host match: {host}")
                return True  # Indicate that the packet should be dropped

        print("HTTP payload:", http_payload)  # Payload is acceptable, continue processing
    except Exception as e:
        print("Error accessing TCP payload:", e)
    return False  # Indicate that the packet should not be dropped
