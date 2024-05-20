#!/usr/bin/env python3

import logging
import time
import struct
import p4runtime_sh.shell as sh
import p4runtime_sh.p4runtime as shp4rt
import p4runtime_shell_utils as shu
from scapy.all import *
from p4runtime_sh.shell import PacketOut
from http_dpi_application import process_http
import keyboard

logger = logging.getLogger(None)
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

global_data = {}

# These values must correspond with ones in the P4 source code
global_data['CPU_PORT'] = 510
global_data['CPU_PORT_CLONE_SESSION_ID'] = 57
global_data['NUM_PORTS'] = 5

def read_blacklist(file_path):
    """Read the blacklist file and return a list of blocked hosts."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def setUp(grpc_addr='0.0.0.0:9559',
          p4info_txt_fname='flowcache.p4info.txt'):
    logger.info("setUp()")
    sh.setup(device_id=0,
             grpc_addr=grpc_addr,
             election_id=(0, 1), # (high_32bits, lo_32bits)
             config=None,
             verbose=False)

    # Create Python dicts from name to integer values, and integer
    # values to names, for the P4_16 serializable enum types
    # PuntReason_t and ControllerOpcode_t once here during setup.
    logger.info("Reading p4info from {}".format(p4info_txt_fname))
    p4info_data = shu.read_p4info_txt_file(p4info_txt_fname)

    global_data['punt_reason_name2int'], global_data['punt_reason_int2name'] = \
        shu.serializable_enum_dict(p4info_data, 'PuntReason_t')
    global_data['opcode_name2int'], global_data['opcode_int2name'] = \
        shu.serializable_enum_dict(p4info_data, 'ControllerOpcode_t')
    logger.debug("punt_reason_name2int=%s" % (global_data['punt_reason_name2int']))
    logger.debug("punt_reason_int2name=%s" % (global_data['punt_reason_int2name']))
    logger.debug("opcode_name2int=%s" % (global_data['opcode_name2int']))
    logger.debug("opcode_int2name=%s" % (global_data['opcode_int2name']))

    global_data['p4info_obj_map'] = shu.make_p4info_obj_map(p4info_data)
    global_data['cpm_packetin_id2data'] = \
        shu.controller_packet_metadata_dict_key_id(global_data['p4info_obj_map'],
                                                   "packet_in")
    logger.debug("cpm_packetin_id2data=%s" % (global_data['cpm_packetin_id2data']))

    global_data['pktin'] = sh.PacketIn()

def tearDown():
    logger.info("tearDown()")
    sh.teardown()

def get_all_packetins(pktin, timeout_sec):
    pktlist = []
    pktin.sniff(lambda p: pktlist.append(p), timeout=timeout_sec)
    return pktlist

def writeCloneSession(clone_session_id, port_list):
    replication_id = 0
    cse = sh.CloneSessionEntry(clone_session_id)
    for p in port_list:
        cse.add(p, replication_id)
    cse.insert()

#############################################################
# Define a few small helper functions that help construct
# parameters for the table_add() method.
#############################################################

def add_flow_cache_entry_action_cached_action(ipv4_proto_int,
                                              ipv4_src_addr_str,
                                              ipv4_dst_addr_str,
                                              port_int,
                                              decrement_ttl_bool,
                                              new_dscp_int):
    te = sh.TableEntry('flow_cache')(action='cached_action')
    te.match['protocol'] = '%s' % (ipv4_proto_int)
    te.match['src_addr'] = ipv4_src_addr_str
    te.match['dst_addr'] = ipv4_dst_addr_str
    te.action['port'] = '%d' % (port_int)
    if decrement_ttl_bool:
        x = 1
    else:
        x = 0
    te.action['decrement_ttl'] = '%d' % (x)
    te.action['new_dscp'] = '%d' % (new_dscp_int)
    te.insert()


setUp()

PUNT_REASON_FLOW_UNKNOWN = global_data['punt_reason_name2int']['FLOW_UNKNOWN']
print(f'Lets whats the result for PUNT_REASON_FLOW_UNKNOWN: {PUNT_REASON_FLOW_UNKNOWN}')
logger.info("Found numeric code %d for punt reason FLOW_UNKNOWN"
            "" % (PUNT_REASON_FLOW_UNKNOWN))

logger.info("Initializing clone session id CPU_PORT_CLONE_SESSION_ID")
try:
    writeCloneSession(global_data['CPU_PORT_CLONE_SESSION_ID'],
                      [global_data['CPU_PORT']])
except shp4rt.P4RuntimeWriteException as e:
    logger.warning("Got exception trying to configure clone session %d."
                   "  Assuming it was initialized already in an earlier"
                   " run of the controller."
                   "" % (global_data['CPU_PORT_CLONE_SESSION_ID']))
tname = 'flow_cache'
n = shu.entry_count(tname)
logger.info("Found %d entries in table '%s'" % (n, tname))
if n > 0:
    shu.delete_all_entries(tname)
    n = shu.entry_count(tname)
    logger.info("After deleting all entries in table '%s' found %d entries"
                "" % (tname, n))

# Helper function to print IP details
def print_details(ip_layer):
    print("\nIP Header Details:")
    print(f"Version: {ip_layer.version}, Header Length: {ip_layer.ihl}, Type of Service: {ip_layer.tos}")
    print(f"Total Length: {ip_layer.len}, Identification: {ip_layer.id}")
    print(f"Flags: {ip_layer.flags}, Fragment Offset: {ip_layer.frag}")
    print(f"Time to Live: {ip_layer.ttl}, Protocol: {ip_layer.proto}")
    print(f"Header Checksum: {ip_layer.chksum}, Source Address: {ip_layer.src}, Destination Address: {ip_layer.dst}")
    print("\n*************************************************\n")

def reception():
    while True:
        if keyboard.is_pressed('s'):  # Check if 's' is pressed
            print("Stopping reception.")
            break  # Exit the while loop
        # Retrieve packet-ins
        pktin_lst = get_all_packetins(global_data['pktin'], 0.0001)
        if not pktin_lst:
            continue

        skip_remaining_packets = False  # Flag to control loop exit

        for pktin in pktin_lst:
            if skip_remaining_packets:
                break  # Exit the for loop early if flagged to skip

            packet = Ether(pktin.packet.payload)  # Decode Ethernet frame
            if packet.haslayer(IP):
                ip_layer = packet[IP]
                print_details(ip_layer)  # Assuming this function prints the details

                if packet.haslayer(TCP):
                    tcp_segment = packet[TCP]
                    if tcp_segment.dport == 80 or tcp_segment.sport == 80:
                        blacklist_hosts = read_blacklist("/home/anthony/HTTP_TEST/p4runtime_based_implementation/p4-guide/flowcache/blacklist.txt")
                        if process_http(packet, blacklist_hosts):
                            logger.info("Dropping packet due to blacklist match.")
                            skip_remaining_packets = True  # Set flag to skip remaining packets
                            break  # Exit the blacklist host loop
                    else:
                        logger.info("TCP packet not on port 80, hence, we assumed that the traffic is not HTTP.")
                else:
                    logger.info("Not a TCP packet, cannot contain HTTP traffic.")
            else:
                logger.info("Not an IP packet, moving on.")

            # If flagged, skip remaining processing for current list of packet-ins
            if skip_remaining_packets:
                break
            print("\n*************************************************")
            pktinfo = shu.decode_packet_in_metadata(global_data['cpm_packetin_id2data'], pktin.packet)
            # Make sure this processing happens inside a loop or function where pktin is defined and contains the packet.
            if pktinfo['metadata']['punt_reason'] == PUNT_REASON_FLOW_UNKNOWN:
                input_port = pktinfo['metadata']['input_port']
                egress_port = 1 if input_port == 0 else 0 if input_port == 1 else None

                # Prepare the binary payload from the received packet_in message
                binary_payload = pktin.packet.payload

                # Initialize PacketOut with binary payload
                pkt_out = sh.PacketOut(payload=binary_payload)

                # Directly set metadata fields, assuming PacketOut's metadata is a dictionary-like interface
                pkt_out.metadata['opcode'] = '1'  # ControllerOpcode_t.SEND_TO_PORT_IN_OPERAND0
                pkt_out.metadata['reserved1'] = '0'
                pkt_out.metadata['operand0'] = str(egress_port)  # This should be a string representation if the API expects it

                # Send the packet_out message
                pkt_out.send()
                logger.info(f"Packet from input port {input_port} instructed to egress port {egress_port}.")

        # Handle outer loop exit or continuation
        if skip_remaining_packets:
            continue  # Immediately start next iteration of while loop

reception()