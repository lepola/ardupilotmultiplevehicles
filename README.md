# Ardupilot SITL multiplevehicles
Simple python script which allow you start multiple SITL vehicles.
First start can take time.
This open vehicles from port 14551 up, and instances from 1 up.

Move *sim_vehicle_mod.py* and *sim_vehicle_multiple.py* to your ardupilot sim_vehicle folder. 
*Example: /vagrant/ardupilot/Tools/autotest/

# How to use?
run command: *python sim_vehicle_multiple.py

Parameters:
-l LOCATION, [x,y,z,heading]
-v FRAME, [ArduPlane, ArduCopter etc..]
-a AMOUNT, amount of vehicles

