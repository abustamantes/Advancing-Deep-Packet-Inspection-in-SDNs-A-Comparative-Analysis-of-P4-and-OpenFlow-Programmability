from mininet.net import Mininet
from mininet.node import Controller, RemoteController, Switch
from mininet.cli import CLI
from mininet.log import setLogLevel

class BMv2Switch(Switch):
    """BMv2 P4 switch with gRPC support"""
    def __init__(self, name, sw_path='/usr/local/bin/simple_switch_grpc', json_path=None, thrift_port=None, grpc_port=50051, pcap_dump=False, **kwargs):
        Switch.__init__(self, name, **kwargs)
        self.sw_path = sw_path
        self.json_path = json_path
        self.thrift_port = thrift_port
        self.grpc_port = grpc_port
        self.pcap_dump = pcap_dump

    def start(self, controllers):
        cmd = [self.sw_path]
        if self.json_path:
            cmd += ['--log-console', '--log-level', 'debug', '--log-flush']
            cmd += ['--', '--grpc-server-addr', '0.0.0.0:%d' % self.grpc_port]
            if self.thrift_port:
                cmd += ['--thrift-port', str(self.thrift_port)]
            if self.pcap_dump:
                cmd += ['--pcap']
            cmd += ['-i 1@%s' % self.name, self.json_path]
        self.cmd(' '.join(cmd) + ' > /tmp/' + self.name + '-bmv2.log 2>&1 &')

    def stop(self):
        self.cmd('kill %' + self.sw_path)
        super(BMv2Switch, self).stop()

def createNetwork():
    net = Mininet(controller=RemoteController)

    # Add controller
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Add BMv2 switch with gRPC support
    s1 = net.addSwitch('s1', cls=BMv2Switch)

    # Add hosts with static MAC addresses
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

    # Add links
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    # Start the network
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    createNetwork()
