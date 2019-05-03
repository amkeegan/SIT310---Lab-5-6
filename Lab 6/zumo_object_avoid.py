#!/usr/bin/env python
import rospy
from std_msgs.msg import Int8
from geometry_msgs.msg import Twist
from std_msgs.msg import Int8
import time
import sys
import os

# imports the MuxSelect service 
from topic_tools.srv import MuxSelect

rospy.init_node('zumo_object_avoid', anonymous=True)

# /zumo/1/cmd_vel - zumo_move_forward
# /zumo/2/cmd_vel - zumo_object_detect subsumes /zumo/1/cmd_vel
# /zumo/3/cmd_vel - zume_object_avoid (This .py) subsumes /zumo/2/cmd_vel

pub = rospy.Publisher('/zumo/3/cmd_vel', Twist, queue_size=3)

current_topic = 0

current_detect = 0


#def stop():
#	vel_msg = Twist()
#	vel_msg.linear.x = 0
#	vel_msg.linear.y = 0
#	vel_msg.linear.z = 0
#	vel_msg.angular.x = 0
#	vel_msg.angular.y = 0
#	vel_msg.angular.z = 0
#	vel_msg.linear.x = 0
#	pub.publish(vel_msg)

def move_left():
	vel_msg = Twist()
	vel_msg.linear.x = 0
	vel_msg.linear.y = 1
	vel_msg.linear.z = 0
	vel_msg.angular.x = 0
	vel_msg.angular.y = 0
	vel_msg.angular.z = 0 
	pub.publish(vel_msg)
	time.sleep(0.1)

def move_right():
	vel_msg = Twist()
	vel_msg.linear.x = 0
	vel_msg.linear.y = -1
	vel_msg.linear.z = 0
	vel_msg.angular.x = 0
	vel_msg.angular.y = 0
	vel_msg.angular.z = 0
	pub.publish(vel_msg)
	time.sleep(0.1)


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


def handle_zumo_detect(wall_msg):
	global current_detect, current_topic
	if(wall_msg.data > 6):
		current_detect = 1
		if (current_topic == 2):
			call_srv('mux_cmdvel_avoid', '/zumo/32/cmd_vel')
			current_topic = 32	
	else:
		current_detect = 0


def handle_zumo_avoid_left(wall_msg):
	global current_topic, current_topic	
	#if (current_detect == 1):	
	if (wall_msg.data > 3): 
		move_right()
		move_right()			
	if(current_detect == 0):
		if (current_topic == 32):
			call_srv('mux_cmdvel_avoid', '/zumo/2/cmd_vel')
			current_topic = 2

def handle_zumo_avoid_right(wall_msg):
	global current_topic, current_detect	
	#if (current_detect == 1):		
	if (wall_msg.data > 3): 			
		move_left()
		move_left()			
	if(current_detect == 0):
		if (current_topic == 32):
			call_srv('mux_cmdvel_avoid', '/zumo/2/cmd_vel')	
			current_topic = 2	

rospy.Subscriber('/zumo/prox_frontleft', Int8, handle_zumo_detect)
rospy.Subscriber('/zumo/prox_frontright', Int8, handle_zumo_detect)
rospy.Subscriber('/zumo/prox_left', Int8, handle_zumo_avoid_left)
rospy.Subscriber('/zumo/prox_right', Int8, handle_zumo_avoid_right)

#take over
#os.system("rosrun topic_tools mux_select mux_cmdvel /zumo/2/cmd_vel")
call_srv('mux_cmdvel_avoid', '/zumo/2/cmd_vel')
current_topic = 2
rospy.spin()
