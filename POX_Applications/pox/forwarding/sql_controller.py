from pox.core import core
import pox.openflow.libopenflow_01 as of
from sql_dpi_application import process_sql

log = core.getLogger()

def read_blacklist(file_path):
    with open(file_path, 'r') as file:
        return set(line.strip() for line in file)

def _handle_PacketIn(event):
    try:
        packet = event.parsed
        if not packet.parsed:
            log.debug("Incomplete packet, ignoring and moving on.")
            return

        if packet.type == packet.IP_TYPE:  # Check if it's an IP packet
            ip_packet = packet.payload  # Access the IP packet
            if ip_packet.protocol == ip_packet.TCP_PROTOCOL:  # Check if it's TCP
                tcp_segment = ip_packet.payload  # Access the TCP segment
                if tcp_segment.dstport == 3306:
                    blacklist_commands = read_blacklist("/home/anthony/pox/pox/forwarding/sql_blacklist.txt")
                    if process_sql(tcp_segment,blacklist_commands):
                        log.info("Dropping packet due to blacklist match.")
                        return  # Drop the packet if process_sql returns True
                else:
                    log.info("TCP packet not on port 3306, hence, we assumed that the traffic is not SQL.")
            else:
                log.info("Not a SQL packet, moving on.")
        else:
            log.info("Not an IP packet, moving on.")

        # If the packet is not dropped, continue with normal processing
        flood_packet(event)
    
    except Exception as e:
        log.error("An error occurred while handling a packet, skipping this one: " + str(e))
        return  # Continue listening and processing new packets

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
