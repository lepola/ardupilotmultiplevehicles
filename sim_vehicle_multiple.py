#!/usr/bin/env python

"""
Framework to start a simulated multiple vehicles.

Panu Haaraniemi, August 2017
"""
import os
import subprocess
import sys
import time
import math

import argparse

# Print colors
startc = '\033[94m'
timec = '\033[1m'
endc = '\033[0m'
buildc = '\033[93m'
finishc = '\033[92m'
checkc = '\033[93m'
startingc = '\033[93m'

startTime = int(round(time.time() * 1000))

processlist = []

progressEnd = 0


# return colored string
def color(stri, col):
	global endc
	return col + str(stri) + endc

#Return up time, format hh:mm:ss
def getTime():
	nowTime = int(round(time.time() * 1000))
	uptime = nowTime - startTime
	
	h = int(math.floor(uptime / 3600000))
	m = int(math.floor((uptime - h*3600000) / 60000))
	s = int(round((uptime - (m * 60000) - (h*3600000)) / 1000))

	if h < 10:
		h = "0" + str(h)
	if m < 10:
		m = "0" + str(m)
	if s < 10:
		s = "0" + str(s)
	return str(h)+":"+str(m)+":"+str(s)

#Return time string, format (hh:mm:ss)
def getTimeStr():
	global timec, endc
	t = color("(" + getTime() + ")", timec)
	return t

# Printing text with uptime, progress and status
def pr(msg, progress, status, blue):
	global startc, endc, startingc, buildc, finishc, checkc, progressEnd
	
	if status is "Build":
		status = "["+color(status,  buildc)+"]"
	if status is "Check":
		status = "["+color(status,  checkc)+"]"
	if status is "Starting":
		status = "["+color(status,  startingc)+"]"
	if status is "Finish":
		status = "["+color(status,  finishc)+"]"

	prog = "[" + color(str(progress) + "/" + str(progressEnd), startc) + "]"

	if blue is 1:
		msg = color(str(msg), startc)

	print(getTimeStr() + "-" + status + prog + " : " + str(msg))


#Getting arguments
parser = argparse.ArgumentParser(description='Settings')
parser.add_argument("-a", "--amount", default=1, type=int, help="Amount of simulated aircrafts")
parser.add_argument("-v", "--version", default="ArduCopter", help="ArduCopter, ArduPlane, ArduRover")
parser.add_argument("-l", "--location", default="62.40251,25.671460,137,0", help="Custom location, lat,lon,alt,heading")

args = parser.parse_args()

progressEnd = args.amount

#Parsing x, y, altitude, heading
locX = float(args.location.split(",")[0])
locY = float(args.location.split(",")[1])
locA = float(args.location.split(",")[2])
locH = float(args.location.split(",")[3])



startRange = 1



def main():
	global startRange, args, locX, locY, locA, locH, progressEnd, processlist

	portString = "["

	# Nothing built, lets build
	if not os.path.isdir("/vagrant/build") or not os.path.isdir("/vagrant/build/sitl/"+args.version+"1"):

		location = str(locX) + "," + str(locY + 0.0001 * 1) + "," + str(locA) + "," + str(locH)
		command_args = ("python /vagrant/Tools/autotest/sim_vehicle_mod.py -v " + args.version + " -I 1"  + " -l " + location).split(" ")
		p = subprocess.Popen(command_args, cwd="/vagrant/ArduCopter", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		processlist.append(p)

		while True:
			nl = p.stdout.readline()
			if nl == '' and p.poll() is not None:
				break
			if "Waiting for heartbeat" in nl:
				break;
			pr(nl.replace('\n', " "), 0, "Build", 0)
		pr("Build done, continuing..", 0 , "Build", 1)
		portString += "14551, "
		startRange = 2

	# Creating folders for multiple instances if not exist
	for i in range(1, args.amount+1):
		global progress, status
		# Checking if arducopter folder exist...
		if not os.path.isdir("/vagrant/" + args.version + str(i)) or not os.path.isdir("/vagrant/build/sitl/" + args.version + str(i)):
			pr("Directory \""+str(args.version) + str(i) + "\" not found", i, "Check", 1)
			pr("Creating \"" + str(args.version) + str(i) + "\" folder...", i , "Check", 1)

		if not os.path.isdir("/vagrant/" + args.version + str(i)):
			command = ("cp -a /vagrant/"+str(args.version) + " /vagrant/" + str(args.version) + str(i)).split(" ")
			result = subprocess.check_output(command)
			print(result)
		if not os.path.isdir("/vagrant/build/sitl/" + args.version + str(i)):
			command = ("cp -a /vagrant/build/sitl/" + str(args.version) + "1 /vagrant/build/sitl/" + str(args.version) + str(i)).split(" ")
			result = subprocess.check_output(command)
			print(result)

	# Starting sim_vehicle processes
	for i in range(startRange, args.amount+1):

		pr("Starting simulation for port " + str(14550+i), i, "Starting", 1)
		location = str(locX) + "," + str(locY + 0.0001 * i) + "," + str(locA) + "," + str(locH)
		command_args = ("python /vagrant/Tools/autotest/sim_vehicle_mod.py -v " + args.version + " -I " + str(i)  + " -l " + location).split(" ")
		p = subprocess.Popen(command_args, cwd="/vagrant/ArduCopter" + str(i), stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Success!

		processlist.append(p)

		while True:
			nl = p.stdout.readline()
			if nl == '' and p.poll() is not None:
				break
			if "Waiting for heartbeat" in nl:
				break;
			pr(nl.replace('\n', ""), i, "Starting", 0)
		pr("Ready: Simulation running in port " + str(14550 + i), i, "Starting", 1)
		portString += str(14550 + i) + ", "

	portString = portString[:-2] + "]"
	pr("Simulation running in ports: " + portString, args.amount, "Finish", 1)
	while True:
		pass

# Main
try:
	main()
except KeyboardInterrupt:
	pr("Shutting down...", 0, "Finish", 1)
	time.sleep(2)
	sys.exit(1)
