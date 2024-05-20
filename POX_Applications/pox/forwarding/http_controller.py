from pox.core import core
import pox.openflow.libopenflow_01 as of
from http_dpi_application import process_http

log = core.getLogger()

def read_blacklist(file_path):
    """Read the blacklist file and return a set of blocked hosts."""
    with open(file_path, 'r') as file:
        return set(line.strip() for line in file)

def _handle_PacketIn(event):
    packet = event.parsed

    if packet.type == packet.IP_TYPE:  # Check if it's an IP packet
        ip_packet = packet.payload  # Access the IP packet
        if ip_packet.protocol == ip_packet.TCP_PROTOCOL:  # Check if it's TCP
            tcp_segment = ip_packet.payload  # Access the TCP segment
            if tcp_segment.dstport == 80 or tcp_segment.srcport == 80:
                blacklist_hosts = read_blacklist("/home/anthony/pox/pox/forwarding/blacklist.txt")
                if process_http(tcp_segment, blacklist_hosts):
                    log.info("Dropping packet due to blacklist match.")
                    return  # Drop the packet if process_http returns True
            else:
                log.info("TCP packet not on port 80, hence, we assumed that the traffic is not HTTP.")
        else:
            log.info("Not a TCP packet, cannot contain HTTP traffic.")
    else:
        log.info("Not an IP packet, moving on.")

    # If the packet is not dropped, continue with normal processing
    flood_packet(event)

def flood_packet(event):
    # Create a packet-out message
    msg = of.ofp_packet_out()
    # Specify the action to flood the packet
    action = of.ofp_action_output(port=of.OFPP_FLOOD)
    msg.actions.append(action)
    # Set the packet data and in_port
    msg.data = event.ofp
    msg.in_port = event.port
    # Send the packet-out message to the switch
    event.connection.send(msg)

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("Reactive hub application is running.")
