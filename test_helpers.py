#!/usr/bin/python3.5

import subprocess


# Create automatically content for ccn-lite
def create_content_auto(num):
	path = "text/text"+str(num)
	name = "text"+str(num)
	content = "This is the content from text: "+str(num)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-mkC -s ndn2013 /node" + str(1) + "/" + path + " > /home/pi/ccn-lite/test/ndntlv/" + name + ".ndntlv << "+content
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Search automatically content for ccn-lite
def search_content_auto(local, num, search_id):
	path = "/node1/text/text"+str(num)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-peek -s ndn2013 -u " + local + "/9998 " + path + " | /home/pi/ccn-lite/build/bin/ccn-lite-pktdump -f 2 > /home/pi/searchlogs/search"+search_id+".log 2>&1 &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return

