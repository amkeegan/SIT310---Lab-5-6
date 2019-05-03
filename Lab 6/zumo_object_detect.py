#!/usr/bin/env python
import rospy
from std_msgs.msg import Int8
from geometry_msgs.msg import Twist
from std_msgs.msg import Int8
import time
import sys
import os

rospy.init_node('zumo_object_detect', anonymous=True)
pub = rospy.Publisher('/zumo/2/cmd_vel', Twist, queue_size=3)

current_topic = 0
new_topic = 1


########################
import rospy
import string 
# imports the MuxSelect service 
from topic_tools.srv import MuxSelect

def call_srv(m, t):
    # There's probably a nicer rospy way of doing this
    s = m + '/select'
    print "Waiting for service \"%s\""%(s)
    rospy.wait_for_service(s)
    print "Selecting \"%s\" at mux \"%s\""%(t, m)
    try:
        srv = rospy.ServiceProxy(s, MuxSelect)
	return srv(t)
    except rospy.ServiceException as e:
        print "Service call failed: %s"%e

############################



def stop():
	vel_msg = Twist()
	vel_msg.linear.x = 0
	vel_msg.linear.y = 0
	vel_msg.linear.z = 0
	vel_msg.angular.x = 0
	vel_msg.angular.y = 0
	vel_msg.angular.z = 0
	vel_msg.linear.x = 0
	pub.publish(vel_msg)

def handle_zumo_sensor(wall_msg):
	global current_topic
	if(wall_msg.data > 6):
		new_topic = 21
		stop() #actually publish a new message..
	else:
		new_topic = 1

	#only change topics if we need to.
	if(current_topic == 1 and new_topic == 21):
		
		call_srv('mux_cmdvel', '/zumo/21/cmd_vel')
		current_topic = 21

	if(current_topic == 21 and new_topic == 1):
		print ('Switching to Channel 1')
		call_srv('mux_cmdvel', '/zumo/1/cmd_vel')
		current_topic = 1

rospy.Subscriber('/zumo/prox_frontleft', Int8, handle_zumo_sensor)
rospy.Subscriber('/zumo/prox_frontright', Int8, handle_zumo_sensor)

#take over
call_srv('mux_cmdvel', '/zumo/1/cmd_vel')
current_topic = 1
rospy.spin()
