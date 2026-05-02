#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist    
    
class ShapeDrawer(Node): # MODIFY NAME
    def __init__(self):
        super().__init__("turtle_shape") # MODIFY NAME
        
        # Create subscriber
        self.subscription_= self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        # Create publisher
        self.publisher_= self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Create timer (1 second = 1 Hz)
        self.timer = self.create_timer(0.05, self.move_turtle)

        #Setting the shape variables
        self.side_no = 4
        self.side_length = 2
        self.angle = (2*math.pi)/self.side_no   #In RADIANS

        #Defining the state variable
        self.state = "Idle"

        #Intialising the trajectory
        self.final_x = 0.0
        self.final_y = 0.0
        self.final_theta = 0.0

        #Setting a pose_callback flag
        self.pose_received = False

        self.threshold = 0.1

    def pose_callback(self, msg):
        #Passing the intial values of turtle only once
        #This if statement wont work once pose_recieved becomes 'True'
        if not self.pose_received:
            self.final_x = msg.x
            self.final_y = msg.y
            self.final_theta = msg.theta
            self.pose_received = True
        
        #Storing all the variable for accessing everywhere else
        #This variables will get refreshed everytime the create_subscription() method calls it
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_theta = msg.theta
        self.current_linear_velocity = msg.linear_velocity
        self.current_angular_velocity = msg.angular_velocity

        

    def move_turtle(self):

        if not self.pose_received:
            return   # wait until first data arrives
    
        #instance for getting values from Twist message type
        cmd = Twist()

        self.theta_corrector()  #calling the theta correction method
        self.path_planning()    #This method gives the next coordinate to move

        #Error calculation
        self.error_x = math.fabs(self.final_x - self.current_x)
        self.error_y = math.fabs(self.final_y - self.current_y)
        self.error_theta = math.fabs(self.final_theta - self.current_theta)
        self.error_distance = math.fabs(math.sqrt((self.error_x)**2 + (self.error_y)**2))
        

        #Setting the state variable to identify if the bot is running
        if(self.error_x < self.threshold and self.error_y < self.threshold and self.error_theta < self.threshold):
            self.state = "Idle"
        elif(self.error_x < self.threshold and self.error_y < self.threshold and self.error_theta != 0):
            self.state = "Turning"
        elif(self.error_x != 0 or self.error_y != 0):
            self.state = "Moving"

        #Moving the bot to destination
        if(self.state == "Idle"):
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
        elif(self.state == "Moving"):
            cmd.linear.x = 1.0
            cmd.angular.z = 0.0
        elif(self.state == "Turning"):
            cmd.linear.x = 0.0
            cmd.angular.z = 1.0
        
        self.get_logger().info(f'error_x: {self.error_x}, state: {self.state}')

        self.publisher_.publish(cmd)
    
    def path_planning(self):
        if(self.state == "Idle"):
            self.final_x += math.cos(self.current_theta)*self.side_length
            self.final_y += math.sin(self.current_theta)*self.side_length
            self.final_theta += self.angle

        self.get_logger().info(f'Current Coordinates -> x: {self.current_x:.2f}, y: {self.current_y:.2f}, theta: {self.current_theta*(180/3.14):.2f}')
        self.get_logger().info(f'Next Waypoint -> x: {self.final_x:.2f}, y: {self.final_y:.2f}, theta: {self.final_theta*(180/3.14):.2f}')
        

    #theta corrector when it goes after +180 it starts to calculate the angle in the CW direction from +ve X-axis
    def theta_corrector(self):
        if(self.current_theta < 0 and self.current_theta >= -(math.pi)):            
            self.current_theta += math.pi*2

        if(self.final_theta > 2*math.pi):
            self.final_theta -= 2*math.pi


def main(args=None):
    rclpy.init(args=args)
    node = ShapeDrawer() # MODIFY NAME
    rclpy.spin(node)
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()