#!/usr/bin/python
import socket
import struct
import GeoIP
import ConfigParser


class ReceiveNetflow():
	def __init__(self, config_file):
		return None

	def configMap(self, section):
		"""
		Parses the config file, uses the following syntax to call a var from the conf:
		configMap("section_title")['var_name']
		REQUIRES: ConfigParser
		"""
		config = ConfigParser.ConfigParser()
		config.read(self.config_file)
		dict1 = {}
		options = config.options(section)
		for option in options:
			try:
				dict1[option] = config.get(section, option)
				if dict1[option] == -1:
					DebugPrint("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1


def addressInNetwork(self, ip, net):
	"""
	Checks if an ip address is in a network, returns bool:
	addressInNetwork("10.0.1.3", "10.0.0.0/8")
	REQUIRES: socket, struct
	"""
	ipaddr = struct.unpack('L',socket.inet_aton(ip))[0]
	netaddr,bits = net.split('/')
	netmask = struct.unpack('L',socket.inet_aton(netaddr))[0] & ((2L<<int(bits)-1) - 1)
	return ipaddr & netmask == netmask


def getGeoIP(self, remote_addr):
	"""
	This function takes the ip address and resolves the geo ip data.
	It returns a tuple with status and msg.  If geo ip data is resolved, the status is true
	the msg is a dict with the following options:
	country_code, country_code3, country_name, city, region, region_name, postal_code, 
	latitude, longitude, area_code, time_zone, metro_code
	REQUIRES: GeoIP
	"""
	gi = GeoIP.open(configMap("netflow")['geoip_dat_path'],GeoIP.GEOIP_STANDARD)
	gir = gi.record_by_addr(remote_addr)

	if gir:
		status = True
		msg = gir
	else:
		status = False
		msg = ''
	return status, msg


def getNetflow(self, data):
	"""
	Takes the UDP netflow data and parses the data out based on netflow v5 offsets
	REQUIRES: Struct
	"""
	result = {}
	lenFlows = (len(data) - 24) / 48
	#version = int(struct.unpack(1*'B', data[1:2])[0])
	#print 'Version:',version
	flows = int(struct.unpack(1*'B', data[3:4])[0])
	#print 'Flows:', flows
	#uptime = struct.unpack(4*'B', data[4:8])
	#print 'Uptime:', uptime
	count = 0
	while ((count < flows) and (flows == lenFlows)):
		offset = (count * 48) + 24
		source = '.'.join(str(n) for n in struct.unpack(4*'B', data[(offset+0):(offset+4)]))
		#print 'Source:', source, '('+getgeoip(source)+')'
		dest = '.'.join(str(n) for n in struct.unpack(4*'B', data[(offset+4):(offset+8)]))
		#print 'Destination:', dest, '('+getgeoip(dest)+')'
		#sport = int(struct.unpack(1*'!H', (data[(offset+32)] + data[(offset+33)]))[0])
		#print 'Sport:', sport
		#dport = int(struct.unpack(1*'!H', data[(offset+34)] + data[(offset+35)])[0])
		#print 'Dport:', dport
		#if (int(struct.unpack(1*'B', data[(offset+38)])[0]) == 6):
		#	prot = 'TCP'
		#elif (int(struct.unpack(1*'B', data[(offset+38)])[0]) == 17):
		#	prot = 'UDP'
		result[count] = source, dest
		count += 1
	return result


def main():

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((configMap("netflow")['udp_ip'], int(configMap("netflow")['udp_port'])))

	# while True:
	# 	data, addr = sock.recvfrom( 1500 )
	# 	for key, val in getNetflow(data).iteritems():
	# 		source = val[0]
	# 		dest = val[1]

	# 		for network in configMap("netflow")['internal_network'].split(','):
	# 			if addressInNetwork(source, network):
	# 				source = configMap("netflow")['wan_ip']
	# 			if addressInNetwork(dest, network):
	# 				dest = configMap("netflow")['wan_ip']					
			
	# 		if source != dest:
	# 			gsstat, gs = getGeoIP(source)
	# 			gdstat, gd = getGeoIP(dest)	
	# 			if gsstat & gdstat:
	# 				print gs['country_code'], '->', gd['country_code']
	# 			else:
	# 				print 'Error: Missing Geo Data'
	# 		elif (source == '255.255.255.255' or dest == '255.255.255.255'):
	# 			print 'Broadcast Traffic'
	# 		elif source == dest:
	# 			print "Internal Traffic"
	# 		else:
	# 			print "UNKNOWN:"
			 
 


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass