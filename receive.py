import socket, struct, GeoIP

GEOIP_DAT_PATH = "./GeoIPCity.dat"
UDP_IP = "10.40.6.40"
UDP_PORT= 2055

def getgeoip(remote_addr):
	
	gi = GeoIP.open(GEOIP_DAT_PATH,GeoIP.GEOIP_STANDARD)

	gir = gi.record_by_addr(remote_addr)

	if not gir:
		msg = '??'
	else:
		msg = gir['latitude'], gir['longitude']
		
		# print gir['country_code']
		# print gir['country_code3']
		# print gir['country_name']
		# print gir['city']
		# print gir['region']
		# print gir['region_name']
		# print gir['postal_code']
		# print gir['latitude']
		# print gir['longitude']
		# print gir['area_code']
		# print gir['time_zone']
		# print gir['metro_code']

	return msg


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind( (UDP_IP, UDP_PORT) )

while True:
	data, addr = sock.recvfrom( 1500 )

	lenFlows = (len(data) - 24) / 48

	version = int(struct.unpack(1*'B', data[1:2])[0])
	#print 'Version:',version

	flows = int(struct.unpack(1*'B', data[3:4])[0])
	#print 'Flows:', flows

	uptime = struct.unpack(4*'B', data[4:8])
	#print 'Uptime:', uptime

	count = 0

	while ((count < flows) and (flows == lenFlows)):

		offset = (count * 48) + 24

		source = '.'.join(str(n) for n in struct.unpack(4*'B', data[(offset+0):(offset+4)]))
		#print 'Source:', source, '('+getgeoip(source)+')'

		dest = '.'.join(str(n) for n in struct.unpack(4*'B', data[(offset+4):(offset+8)]))
		#print 'Destination:', dest, '('+getgeoip(dest)+')'

		sport = int(struct.unpack(1*'!H', (data[(offset+32)] + data[(offset+33)]))[0])
		#print 'Sport:', sport
		
		dport = int(struct.unpack(1*'!H', data[(offset+34)] + data[(offset+35)])[0])
		#print 'Dport:', dport

		if (int(struct.unpack(1*'B', data[(offset+38)])[0]) == 6):
			prot = 'TCP'
		elif (int(struct.unpack(1*'B', data[(offset+38)])[0]) == 17):
			prot = 'UDP'

		print getgeoip(source), '->', getgeoip(dest)

		count += 1
