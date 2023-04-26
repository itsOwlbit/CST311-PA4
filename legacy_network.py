#!/usr/bin/python

# Names: Kevin Mcnulty, Nadia Rahbany, Juli Shinozuka, and Andrew Shiraki
# Date: June 16, 2022
# Title: Legacy Network PA4
# Description: This program creates a mininet topology with three connected legacy routers.
# One edge router is connected to the west coast switch and hosts (h1, h2).  The other edge
# router is connected to the east coast switch and hosts (h3, h4).  A tls webserver runs
# on h3.  The chat server runs on h4.  The chat clients are h1 and h2.

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
#Import makeTerm function from term library
from mininet.term import makeTerm
#kevin needs this
import time
#use this to get pwd
import os

from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    # moved switches (s1, s2) before the legacy routers(r3, r4, r5) for initiliazing
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    # west coast router
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.1/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')
    r3.cmd('ip addr add 192.168.1.2/30 dev r3-eth1')
    # internet router
    r4 = net.addHost('r4', cls=Node, ip='192.168.1.1/30')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r4.cmd('ip addr add 192.168.2.1/30 dev r4-eth1')
    # east coast router
    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    r5.cmd('ip addr add 192.168.2.2/30 dev r5-eth1')

    info( '*** Add hosts\n')
    # west coast hosts with subnet 10.0.1.0/24
    # default route: r3
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.100/24', defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.1.200/24', defaultRoute='via 10.0.1.1')
    # east coast hosts with subnet 10.0.2.0/24
    # default route: r5
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.100/24', defaultRoute='via 10.0.2.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.200/24', defaultRoute='via 10.0.2.1')

    info( '*** Add links\n')
    # west coast links
    net.addLink(r3, s1)
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    # east coast links
    net.addLink(r5, s2)
    net.addLink(s2, h3)
    net.addLink(s2, h4)
    # west coast (r3) connect to internet (r4)
    net.addLink(r3, r4,
        intfname1='r3-eth1', params1={'ip': '192.168.1.2/30'},
        intfname2='r4-eth0', params2={'ip': '192.168.1.1/30'})
    # east coast (r5) connect to internet (r4)
    net.addLink(r4, r5,
        intfname1='r4-eth1', params1={'ip': '192.168.2.1/30'},
        intfname2='r5-eth1', params2={'ip': '192.168.2.2/30'})

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])

    info( '*** Post configure switches and hosts\n')

    # Adding static routes
    r4.cmd('route add -net 10.0.1.0/24 gw 192.168.1.2')
    r4.cmd('route add -net 10.0.2.0/24 gw 192.168.2.2')
    r3.cmd('route add -net 192.168.2.0/30 gw 192.168.1.1')
    r5.cmd('route add -net 192.168.1.0/30 gw 192.168.2.1')
    r3.cmd('route add -net 10.0.2.0/24 gw 192.168.1.1')
    r5.cmd('route add -net 10.0.1.0/24 gw 192.168.2.1')
    
    info( '*** Routing Table on West Coast Router:\n' )
    print net[ 'r3' ].cmd( 'route' )

    info( '*** Routing Table on East Coast Router:\n' )
    print net[ 'r5' ].cmd( 'route' )
    
    #I need the fully qualified path to chat files
    PATH=os.path.abspath(os.path.dirname(__file__))
    
    # copies root CA cert to the directory ca-certificates changing to crt extension
    cmd = 'cp '+PATH+'/server-cert/cacert.pem /usr/local/share/ca-certificates/cacert.crt'
    os.system(cmd)
    # run the ca-certificates application
    cmd = 'update-ca-certificates'
    os.system(cmd)
    # to remove --no-check-certificate error purge package out
    cmd = 'dpkg --purge --force-depends ca-certificates > /dev/null 2>&1'
    os.system(cmd)
    # reinstsall
    cmd = 'apt-get -f install -y > /dev/null 2>&1'
    os.system(cmd)
    
    #Start chat server on h4 in xterm
    makeTerm(h4, title='ChatSrver', term='xterm', display=None, cmd='python3 '+PATH+ '/ServerChat.py')
    #Start tlsWebserver on h2
    makeTerm(h2, title='tlsWebserver', term='xterm', display=None, cmd='python3 ' +PATH+ '/tlswebserver.py' )
    #Bonus line to do the wget and print
    print(h1.cmd('sleep 1 && wget https://10.0.1.200:4443'))
    #maketerm to open xterms on h1 and h3
    #Add 2 second sleep on clients because they were starting before server was ready
    makeTerm( h1, title='ChatClient', term='xterm', display=None, cmd='sleep 2 && python3 '+PATH+'/ClientChat.py' )
    makeTerm( h3, title='ChatClient', term='xterm', display=None, cmd='sleep 2 && python3 '+PATH+'/ClientChat.py' )

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
