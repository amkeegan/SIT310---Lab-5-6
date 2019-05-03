#define USE_USBCON
#include <Wire.h>
#include <Zumo32U4.h>
#include <ros.h>
#include <geometry_msgs/Twist.h>
#include <std_msgs/Int8.h>
ros::NodeHandle nh;
Zumo32U4ProximitySensors proxSensors;
bool proxLeftActive;
bool proxFrontActive;
bool proxRightActive;

std_msgs::Int8 prox_msg;

ros::Publisher pub_left("/zumo/prox_left", &prox_msg);
ros::Publisher pub_frontleft("/zumo/prox_frontleft", &prox_msg);
ros::Publisher pub_frontright("/zumo/prox_frontright", &prox_msg);
ros::Publisher pub_right("/zumo/prox_right", &prox_msg);

void ros_handler( const geometry_msgs::Twist& cmd_msg) 
{
  float x = cmd_msg.linear.x;
  float y = cmd_msg.linear.y;
  int speed = 100;
  if(x == 1.0) forward(speed);
  if(x == -1.0) backward(speed);
  if(y == 1.0) left(speed);
  if(y == -1.0) right(speed);
  stop();
}

ros::Subscriber<geometry_msgs::Twist> sub("/zumo/cmd_vel", ros_handler);
Zumo32U4Motors motors;

void setup()
{
  nh.initNode();
  nh.subscribe(sub);
  nh.advertise(pub_left);
  nh.advertise(pub_frontleft);
  nh.advertise(pub_frontright);
  nh.advertise(pub_right);
  proxSensors.initThreeSensors();
  uint16_t defaultBrightnessLevels[] = {1,2,3,4,5,6,7,8,9,10};
  proxSensors.setBrightnessLevels(defaultBrightnessLevels, 10);
}

void publishSensorData()
{
  prox_msg.data = proxSensors.countsLeftWithLeftLeds();
  pub_left.publish( &prox_msg);
  prox_msg.data = proxSensors.countsFrontWithLeftLeds();
  pub_frontleft.publish( &prox_msg);
  prox_msg.data = proxSensors.countsFrontWithRightLeds();
  pub_frontright.publish( &prox_msg);
  prox_msg.data = proxSensors.countsRightWithRightLeds();
  pub_right.publish( &prox_msg);
}

void forward(int time)
{
  motors.setLeftSpeed(100);
  motors.setRightSpeed(100);
  delay(time);
}

void backward(int time)
{
  motors.setLeftSpeed(-100);
  motors.setRightSpeed(-100);
  delay(time);
}

void left(int time)
{
  motors.setLeftSpeed(-100);
  motors.setRightSpeed(100);
  delay(time);
}

void right(int time)
{
  motors.setLeftSpeed(100);
  motors.setRightSpeed(-100);
  delay(time);
}

void stop()
{
  motors.setLeftSpeed(0);
  motors.setRightSpeed(0);
}

void loop()
{
  static uint16_t lastSampleTime = 0;
  if ((uint16_t)(millis() - lastSampleTime) >= 100)
  {
    lastSampleTime = millis();
    // Send IR pulses and read the proximity sensors.
    proxSensors.read();
    publishSensorData();
  }
  
  nh.spinOnce();
  delay(1);
}
