//P4_16
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_ARP = 0x0806;
const bit<16> TYPE_IPV4 = 0x0800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  reserved;
    bit<9>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
    bit<96> options;
}

header arp_t {
    bit<16> hwtype;
    bit<16> protoType;
    bit<8> hwlen;
    bit<8> protolen;
    bit<16> opcode;
    bit<48> hwsrc;
    bit<32> protosrc;
    bit<48> hwdst;
    bit<32> protodst;
}

header icmp_t {
    bit<8> type;
    bit<8> code;
    bit<16> checksum;
    bit<16> identifier;
    bit<16> seqNo;
}

header sql_t {
    bit<56> payload_start;
    bit<128> query_type;
}

header http_t{
    bit<128> method;
    bit<240> host;
}

struct metadata {
    bool apply_dst_tcp_port_3306;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    tcp_t        tcp;
    arp_t        arp;
    sql_t        sql;
    http_t http;
    icmp_t icmp;
    
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            TYPE_ARP: parse_arp;
            default: accept;
        }
    }

    state parse_ipv4 {
    packet.extract(hdr.ipv4);
    transition select(hdr.ipv4.protocol) {
        6: parse_tcp; // TCP protocol number
        1: parse_icmp;
        default: accept;
    }
    }

    state parse_arp {
        packet.extract(hdr.arp);
        transition accept; 
    }

    state parse_icmp {
        packet.extract(hdr.icmp);
        transition accept; 
    }

    state parse_tcp {
        packet.extract(hdr.tcp);
        transition select(hdr.tcp.dstPort) {
            3306: parse_sql;
            default: accept;
        //transition accept;
    }}

    state parse_http {
        packet.extract(hdr.http); // Extract the custom header
        transition accept;
    }
    state parse_sql {
        packet.extract(hdr.sql); // Extract the custom header
        transition accept;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }

}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action forward(egressSpec_t port){
        standard_metadata.egress_spec = port;
    }

    action forward_method(egressSpec_t port){
        standard_metadata.egress_spec = port;
    }

    action arp_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }

    action set_apply_dst_tcp_port_3306() {
        meta.apply_dst_tcp_port_3306 = true;
    }


    table filter_method {
        key = {
            standard_metadata.ingress_port: exact;
            hdr.sql.query_type: ternary;
        }
        actions = {
            forward_method;
            drop;
            set_apply_dst_tcp_port_3306;
        }
        size = 256;
        default_action = set_apply_dst_tcp_port_3306();
        //default_action = drop();
    }

    table src_tcp_port_3306 {
        key = {
            standard_metadata.ingress_port: exact;
            hdr.tcp.srcPort: exact;           // Source TCP port
        }
        actions = {
            forward;  // Action to forward packet
            drop;     // Action to drop packet
        }
        size = 256;
        default_action = drop();
    }

    table dst_tcp_port_3306 {
        key = {
            standard_metadata.ingress_port: exact;
            hdr.tcp.dstPort: exact;           // Source TCP port
        }
        actions = {
            forward;  // Action to forward packet
            drop;     // Action to drop packet
        }
        size = 256;
        default_action = drop();
    }

    table arp_table {
        key = {
            hdr.arp.opcode: exact; // Match on the ARP opcode
            standard_metadata.ingress_port: exact;
        }
        actions = {
            arp_forward; // Action to forward ARP packets
            drop;
        }
        size = 256;
        default_action = drop();
    }

    table icmp_table {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            forward; // Action to forward packets
            drop;
        }
        size = 256;
        default_action = drop();
    }

    apply {
        if (hdr.arp.isValid()) {
            arp_table.apply();
        } 
        else if (hdr.ipv4.isValid() && hdr.icmp.isValid()) {
            icmp_table.apply(); 
        }
        else if (hdr.tcp.isValid()){
            // Check for TCP source port 3306
            if (hdr.tcp.srcPort == 3306) {
                src_tcp_port_3306.apply();
            } else if (hdr.tcp.dstPort == 3306) {
                filter_method.apply();
                if (meta.apply_dst_tcp_port_3306) {
                    dst_tcp_port_3306.apply();
                }
            } else {
                drop();
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply { }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.arp);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.icmp);
        packet.emit(hdr.tcp);
        packet.emit(hdr.sql);
        packet.emit(hdr.http);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
