from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def customTopo():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    # Add a remote controller
    c0 = net.addController('c0', controller=RemoteController, ip='0.0.0.0')

    # Add two hosts with specified IP addresses
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    # Add a switch with OpenFlow 1.0 support
    s1 = net.addSwitch('s1', protocols='OpenFlow10')

    # Create links between hosts and switch
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    # Start the network
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTopo()
