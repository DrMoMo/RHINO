#!/usr/bin/python
import socket
import struct
import GeoIP
import ConfigParser

class ReceiveNetflow():
  """
  Takes 1 parameter: the config file, usually rhino.conf
  """
  def __init__(self, config_file):
    self.config_file = config_file

  def configMap(self, section):
    """
    Parses the config file, uses the following syntax to call a var from the conf:
    configMap("section_title")['var_name']
    REQUIRES: ConfigParser
    """   
    self.config = ConfigParser.ConfigParser()
    self.config.read(self.config_file)
    self.dict1 = {}
    self.options = self.config.options(section)
    for option in self.options:
      try:
        self.dict1[option] = self.config.get(section, option)
        if self.dict1[option] == -1:
          DebugPrint("skip: %s" % option)
      except:
        print("exception on %s!" % option)
        self.dict1[option] = None
    return self.dict1


  def addressInNetwork(self, ip, net):
    """
    Checks if an ip address is in a network, returns bool:
    addressInNetwork("10.0.1.3", "10.0.0.0/8")
    REQUIRES: socket, struct
    """
    self.ipaddr = struct.unpack('L',socket.inet_aton(ip))[0]
    self.netaddr, self.bits = net.split('/')
    self.netmask = struct.unpack('L',socket.inet_aton(self.netaddr))[0] & ((2L<<int(self.bits)-1) - 1)
    return self.ipaddr & self.netmask == self.netmask


  def getGeoIP(self, remote_addr):
    """
    This function takes the ip address and resolves the geo ip data.
    It returns a tuple with status and msg.  If geo ip data is resolved, the status is true
    the msg is a dict with the following options:
    country_code, country_code3, country_name, city, region, region_name, postal_code, 
    latitude, longitude, area_code, time_zone, metro_code
    REQUIRES: GeoIP
    """
    self.gi = GeoIP.open(self.configMap("netflow")['geoip_dat_path'],GeoIP.GEOIP_STANDARD)
    self.gir = self.gi.record_by_addr(remote_addr)
    if self.gir:
      self.status = True
      self.msg = self.gir
    else:
      self.status = False
      self.msg = ''
    return self.status, self.msg  


  def getNetflow(self):
    """
    Opens a socket to listen for netflow data.
    REQUIRES: socket
    """
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind((self.configMap("netflow")['udp_ip'], int(self.configMap("netflow")['udp_port'])))
    self.data, self.address = self.sock.recvfrom( 1500 )
    return self.data


  def parseNetflow(self, data):
    """
    Takes the UDP netflow data and parses the data out based on netflow v5 offsets
    REQUIRES: Struct
    """
    self.result = {}
    self.lenFlows = (len(data) - 24) / 48
    self.flows = int(struct.unpack(1*'B', data[3:4])[0])
    #self.version = int(struct.unpack(1*'B', data[1:2])[0])
    #self.uptime = struct.unpack(4*'B', data[4:8])
    self.count = 0
    while ((self.count < self.flows) and (self.flows == self.lenFlows)):
      self.offset = (self.count * 48) + 24
      self.source = '.'.join(str(n) for n in struct.unpack(4*'B', data[(self.offset+0):(self.offset+4)]))
      self.dest = '.'.join(str(n) for n in struct.unpack(4*'B', data[(self.offset+4):(self.offset+8)]))
      #self.sport = int(struct.unpack(1*'!H', (data[(self.offset+32)] + data[(self.offset+33)]))[0])
      #self.dport = int(struct.unpack(1*'!H', data[(self.offset+34)] + data[(self.offset+35)])[0])
      #if (int(struct.unpack(1*'B', data[(self.offset+38)])[0]) == 6):
      # self.prot = 'TCP'
      #elif (int(struct.unpack(1*'B', data[(self.offset+38)])[0]) == 17):
      # self.prot = 'UDP'
      self.result[self.count] = self.source, self.dest
      self.count += 1
    return self.result

  
  def Netflow2GeoIPData(self, parsedData):
    """
    This function iterates through a parsed netflow stream and prepares
    the data for use.
    REQUIRED: (pending)
    """
    self.count = 0
    for key, val in parsedData.iteritems():
      self.source = val[0]
      self.dest = val[1]
      for network in self.configMap("netflow")['internal_network'].split(','):
        if self.addressInNetwork(self.source, network):
          self.source = self.configMap("netflow")['wan_ip']
        if self.addressInNetwork(self.dest, network):
          self.dest = self.configMap("netflow")['wan_ip']     
      if self.source != self.dest:
        self.gsstat, self.gs = self.getGeoIP(self.source)
        self.gdstat, self.gd = self.getGeoIP(self.dest) 
        if self.gsstat & self.gdstat:
          self.result[self.count] = True, self.source, self.dest, self.gs, self.gd
        else:
          self.result[self.count] = False, 'Error: Missing Geo Data'
      # need to fix this so it's the last octet = 255
      elif (self.source == '255.255.255.255' or self.dest == '255.255.255.255'):
        self.result[self.count] = False, 'Broadcast Traffic'
      elif self.source == self.dest:
        self.result[self.count] = False, 'Internal Traffic'
      else:
        self.result[self.count] = False, 'UNKNOWN:', self.source, self.dest
      self.count += 1
    return self.result


  def run(self):
    """
    Run, runs the show =)
    """
    while True:
      self.data = self.getNetflow()
      self.parsedData = self.parseNetflow(self.data)
      print self.Netflow2GeoIPData(self.parsedData)