from scapy.all import *

def process_http(packet, blacklist_hosts):
    try:
        if packet.haslayer(Raw):
            payload_data = packet[Raw].load
            print("\nPayload Data:")
            http_payload = payload_data.decode('utf-8')
            # Check if it's a GET request and extract the host
            if "GET " in http_payload:
                # Extracting the host from the HTTP header
                host_start = http_payload.find("Host: ") + 6
                host_end = http_payload.find("\r\n", host_start)
                host = http_payload[host_start:host_end].strip()

                # Check if the host is in the blacklist set
                if host in blacklist_hosts:
                    print("Dropping packet due to host match.")
                    return True  # Indicate that the packet should be dropped
            print("HTTP payload:", http_payload)  # Payload is acceptable, continue processing
    except Exception as e:
        print("Error accessing TCP payload:", e)
    return False  # Indicate that the packet should not be dropped