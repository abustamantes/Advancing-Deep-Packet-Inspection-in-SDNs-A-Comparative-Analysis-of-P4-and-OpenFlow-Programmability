from mininet.net import Mininet
from mininet.node import Controller, RemoteController, Switch
from mininet.cli import CLI
from mininet.log import setLogLevel

class BMv2Switch(Switch):
    """BMv2 P4 switch"""
    def __init__(self, name, sw_path='path/to/bmv2/simple_switch', json_path=None, thrift_port=None, pcap_dump=False, **kwargs):
        Switch.__init__(self, name, **kwargs)
        self.sw_path = sw_path
        self.json_path = json_path
        self.thrift_port = thrift_port
        self.pcap_dump = pcap_dump

    @staticmethod
    def setup():
        # Ensure that the BMv2 path is valid
        pass

    def start(self, controllers):
        cmd = [self.sw_path]
        if self.json_path:
            cmd += ['--log-console', '--log-level', 'debug', '--log-flush', '--', '-i 1@%s' % self.name]
            if self.thrift_port:
                cmd += ['--thrift-port', str(self.thrift_port)]
            if self.pcap_dump:
                cmd += ['--pcap']
            cmd += [self.json_path]
        self.cmd(' '.join(cmd) + ' > /tmp/' + self.name + '-bmv2.log 2>&1 &')

    def stop(self):
        self.cmd('kill %' + self.sw_path)
        super(BMv2Switch, self).stop()

def createNetwork():
    net = Mininet(controller=RemoteController)

    # Add controller
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Add BMv2 switch
    s1 = net.addSwitch('s1', cls=BMv2Switch, sw_path='/usr/local/bin/simple_switch', json_path='/home/absuarez/mininet/Labs/lab7/lab7.json')

    # Add hosts with static MAC addresses
    h1 = net.addHost('h1', ip='192.168.118.138/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='192.168.118.139/24', mac='00:00:00:00:00:02')
    #h3 = net.addHost('h3', ip='20.0.0.1/8', mac='00:00:00:00:00:20')

    # Add links
    net.addLink(h1, s1)
    net.addLink(s1, h2)
    #net.addLink(s1, h3)

    # Start the network
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    createNetwork()
