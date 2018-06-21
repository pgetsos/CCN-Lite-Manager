#!/usr/bin/python3.5

from ccn_config import SERVER_NODE
import subprocess


# Create automatically content for ccn-lite with a specific path
def create_content_auto(num):
	path = "text/text"+str(num)
	name = "text"+str(num)
	content = "This is the content from text: "+str(num)

	bash_command = "echo "+content+" > /home/pi/data/data"+str(num)+".txt "
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)

	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-mkC -s ndn2013 -i /home/pi/data/data"+str(num)+".txt -o /home/pi/ccn-lite/test/ndntlv/" + name + ".ndntlv /node" + str(SERVER_NODE) + "/" + path
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Create automatically content for ccn-lite with dynamic node input
def create_content_auto_with_node(num, node):
	path = "text/text"+str(num)
	name = "text"+str(num)
	content = "This is the content from text: "+str(num)

	bash_command = "echo "+content+" > /home/pi/data/data"+str(num)+".txt"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)

	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-mkC -s ndn2013 -i /home/pi/data/data"+str(num)+".txt -o /home/pi/ccn-lite/test/ndntlv/" + name + ".ndntlv /node" + str(node) + "/" + path
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Search automatically content for ccn-lite
def search_content_auto(local, num, search_id):
	path = "\"/node" + SERVER_NODE + "/text/text"+str(num)+"\""
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-peek -s ndn2013 -u " + local + "/9998 " + path + " | /home/pi/ccn-lite/build/bin/ccn-lite-pktdump -f 2 > /home/pi/searchlogs/search"+search_id+".log 2>&1 &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Create content for ccn-lite
def create_content(node):
	path = input("Local path (don't include initial '/'): ")
	name = input("File name: ")
	content = input("Content: ")

	bash_command = "echo " + content + " > /home/pi/data/data_creation.txt"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)

	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-mkC -s ndn2013 -i /home/pi/data/data_creation.txt -o /home/pi/ccn-lite/test/ndntlv/" + name + ".ndntlv /node" + str(node) + "/" + path
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Search content for ccn-lite
def search_content(local):
	path = input("Lookup path: ")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-peek -s ndn2013 -u " + local + "/9998 " + path + " | /home/pi/ccn-lite/build/bin/ccn-lite-pktdump -f 2 "
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return
