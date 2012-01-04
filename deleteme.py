#!/usr/bin/python
import socket
import struct
import GeoIP
import ConfigParser


config = ConfigParser.ConfigParser()
config.read('rhino.conf')

def configMap(section):
	"""
	Parses the config file, uses the following syntax to call a var from the conf:
	configMap("section_title")['var_name']
	REQUIRES: ConfigParser
	"""
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


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((configMap("netflow")['udp_ip'], int(configMap("netflow")['udp_port'])))
while True:
	data, addr = sock.recvfrom( 1500 )
	print data