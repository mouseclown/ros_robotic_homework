#!/usr/bin/python3



# A very basic TurtleBot script that moves TurtleBot forward indefinitely. Press CTRL + C to stop.  To run:
# On TurtleBot:
# roslaunch turtlebot_bringup minimal.launch
# On work station:
# python goforward.py

import sys
import math
import rospy
import tf
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Path



class Turtlebot():
    def __init__(self):
       
        
        # Create a publisher which can "talk" to TurtleBot and tell it to move
        # Tip: You may need to change the topic name depending on the model of the robot you are using or the configuration from /cmd_vel to the appropiate one
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)

        self.listener = tf.TransformListener()
        self.mindist = 0.2

        # TODO 2: Create a path subscriber and make the turtlebot able to reach a continuous path
        self.path_subscriber = rospy.Subscriber('/path', Path, self.callbackPath)
        
        self.path = None
        self.current_wp = -1   # Our counter to current waypoint
    
    def callbackPath(self, msg):
        rospy.loginfo("Path received. Number of points: %d", len(msg.poses))
        #TODO 2: Define the actions that should be carried out whenever a path is received
        # Hint: If no path is received it is set to None in the constructor (path received) 
        # And also reset the current wp counter (you can set it to the closest point to the robot)
        self.path = msg
        #initial variable definition
        k=0
        self.curr_wp = 0
        distance = 0
        while distance<self.mindist:

            curr_pose =self.path.poses[k]
            curr_pose.header.frame_id = "map"
            curr_pose.header.stamp = rospy.Time()

            try:
                base_goal = self.listener.transformPose('base_link', curr_pose)
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                rospy.loginfo("Problem TF")
                return
            distance = math.sqrt((base_goal.pose.position.x)^2 + (base_goal.pose.position.y)^2)
                                 
            k+=1

        self.curr_wp=k
        rospy.loginfo("Current waypoint: %d", self.curr_wp)

   
   
    def command(self,gx, gy):
        rospy.loginfo("Command")

        goal = PointStamped()
        base_goal = PointStamped()
        # put the control law here from !! 
        angular = 0.0
        linear = 0.0
        # TODO 2: If a path has been received, you should ignore
        # gx and gy and get the coordinates from the current waypoint 
        # Before that, you should update the current waypoint if its near enough
        if self.path is not None:

            goal.header.frame_id = "map"

            goal.header.stamp = rospy.Time()
            goal.point.x = self.path.poses[self.curr_wp].pose.position.x
            goal.point.y = self.path.poses[self.curr_wp].pose.position.y
            goal.point.z = 0.0

            try:
                base_goal = self.listener.transformPoint('base_link', goal)
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                rospy.loginfo("Problem TF")
                return
            #we change the maximum angular rate and maximum velocity so that our magabot's encoders and IMU don't commit as much mistakes.
            angular = math.atan2(base_goal.point.y, base_goal.point.x)
            if math.fabs(angular)>0.3:
                angular = 0.3*(angular/math.fabs(angular))
            if math.fabs(angular)<0.2:
                linear = 0.15
            distance = math.sqrt((base_goal.point.x)**2 + (base_goal.point.y)**2)
            if distance < self.mindist:
                #change the counter of the next waypoint so that it makes jumps of 5 os that control is smoother
                self.curr_wp =self.curr_wp + 5 
                if self.curr_wp >= len(self.path.poses):
                    self.curr_wp = len(self.path.poses) - 1
                    angular = 0.0
                    linear = 0.0
                rospy.loginfo("current_wayp: %d",self.curr_wp)

        
        rospy.loginfo(angular)
        
        self.publish(linear,angular)

    def publish(self,lin_vel, ang_vel):
        # Twist is a datatype for velocity
        move_cmd = Twist()
        # let's go forward at 0.2 m/s
        move_cmd.linear.x = lin_vel
        # let's turn at 0 radians/s
        move_cmd.angular.z = ang_vel

        self.cmd_vel.publish(move_cmd)
        
    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Stop TurtleBot")
        # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
        self.cmd_vel.publish(Twist())
        # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
        rospy.sleep(1)
 
if __name__ == '__main__':
    #try:
        # initiliaze
        rospy.init_node('robotcontrol', anonymous=False)

        # tell user how to stop TurtleBot
        rospy.loginfo("To stop TurtleBot CTRL + C")

        robot=Turtlebot()
        # What function to call when you ctrl + c    
        rospy.on_shutdown(robot.shutdown)

        goalx=0.0
        goaly=0.0

        # TODO 1: Load more internal parameters such as maximum speed, goal tolerance....

        print(' Goal to reach: ', goalx, ', ', goaly)

        #TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
        r = rospy.Rate(10)

        # as long as you haven't ctrl + c keeping doing...
        while not rospy.is_shutdown():
            rospy.loginfo("Loop")
            # publish the velocity
            robot.command(goalx,goaly)
            # wait for 0.1 seconds (10 HZ) and publish again
            r.sleep()

    #except:
    #    rospy.loginfo("robotcontrol node terminated.")
