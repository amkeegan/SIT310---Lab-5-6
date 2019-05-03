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

rospy.init_node('zumo_object_back', anonymous=True)

# /zumo/1/cmd_vel - zumo_move_forward
# /zumo/2/cmd_vel - zumo_object_detect subsumes /zumo/1/cmd_vel
# /zumo/3/cmd_vel - zumo_object_avoid subsumes /zumo/2/cmd_vel
# /zumo/4/cmd_vel - zumo_object_back (This .py) subsumes /zumo/3/cmd_vel

pub = rospy.Publisher('/zumo/4/cmd_vel', Twist, queue_size=3)

front_left = 0
front_right = 0
left = 0
right = 0

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

def move_back():
	vel_msg = Twist()
	vel_msg.linear.x = -1
	vel_msg.linear.y = 0
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


def trapped():
	#print ('Left: ' + str(left) + 'FL: ' + str(front_left) + 'FR: ' +str(front_right) + 'Right: ' + str(right))
	if (front_left < 6): return False
	if (front_right <6): return False
	if (left < 6): return False
	if (right < 6): return False
	else: 
		#print ('I am TRAPPED')
		call_srv('mux_cmdvel_back', '/zumo/4/cmd_vel')
		return True

def back_away():	
	stop()
	move_back()
	if (left > right): move_right()
	else: move_left()
	call_srv('mux_cmdvel_back', '/zumo/3/cmd_vel')

def handle_zumo_detect_fl(wall_msg):
	global front_left
	front_left = wall_msg.data
	if trapped(): back_away()

def handle_zumo_detect_fr(wall_msg):
	global front_right
	front_right = wall_msg.data
	if trapped(): back_away()

def handle_zumo_detect_left(wall_msg):
	global left
	left = wall_msg.data
	if trapped(): back_away()

def handle_zumo_detect_right(wall_msg):
	global right
	right = wall_msg.data
	if trapped(): back_away()

rospy.Subscriber('/zumo/prox_frontleft', Int8, handle_zumo_detect_fl)
rospy.Subscriber('/zumo/prox_frontright', Int8, handle_zumo_detect_fr)
rospy.Subscriber('/zumo/prox_left', Int8, handle_zumo_detect_left)
rospy.Subscriber('/zumo/prox_right', Int8, handle_zumo_detect_right)
#rospy.Subscriber('/zumo/prox_left', Int8, handle_zumo_avoid_left)
#rospy.Subscriber('/zumo/prox_right', Int8, handle_zumo_avoid_right)

#take over
call_srv('mux_cmdvel_back', '/zumo/3/cmd_vel')
#current_topic = 2 ????
rospy.spin()
