from mininet.net import Mininet
from mininet.node import OVSKernelSwitch,OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def simpleTopologyNoController():
    "Create a network without a controller"
    net = Mininet(switch=OVSBridge, controller=None)

    # Add hosts and switch
    h1 = net.addHost('h1', ip='192.168.118.138/24')
    h2 = net.addHost('h2', ip='192.168.118.139/24')
    s1 = net.addSwitch('s1')

    # Add links
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    # Start network
    net.start()
    # Drop to CLI
    CLI(net)

    # Stop network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simpleTopologyNoController()
