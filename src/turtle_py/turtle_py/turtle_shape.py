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
        self.side_no = 6
        self.side_length = 3
        self.angle = (2*math.pi)/self.side_no   #In RADIANS

        #Defining the state variable
        self.state = "Idle"

        #Intialising the trajectory planning variables
        self.final_x = 0.0
        self.final_y = 0.0
        self.final_theta = 0.0

        #Setting a pose_callback flag
        self.pose_received = False

        #Bot Linear Variables
        self.max_linear_speed = 2.5   # 1 m/s
        self.bot_linear_speed = 0.0
        self.accel = 0.4   # 0.2 m/s^2
        self.deccel = 1.0   # 0.5 m/s^2

        #Bot Angular Variables
        self.max_angular_speed = 0.4    # 0.5 rad/s
        self.bot_angular_speed = 0.0
        self.a_turn = 0.1   #Turning acceleration
        self.d_turn = 0.2   #Turning deceleration

        self.Kp = 0.2
        self.turn_Kp = 0.2
        self.threshold = 0.01
        self.threshold_angle = 0.01

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
        self.error_distance = math.sqrt((self.error_x)**2 + (self.error_y)**2)
        

        #Setting the state variable to identify if the bot is running
        if(self.error_distance < self.threshold and self.error_theta < self.threshold_angle):
            self.state = "Idle"
        elif(self.error_x < self.threshold and self.error_y < self.threshold and self.error_theta != 0):
            self.state = "Turning"
        elif(self.error_distance != 0):
            self.state = "Moving"

        
        #Moving the bot to destination
        if(self.state == "Idle"):
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        elif(self.state == "Moving"):
            cmd.linear.x = self.move_forward()
            cmd.angular.z = 0.0
            self.bot_angular_speed = 0.0

        elif(self.state == "Turning"):
            cmd.linear.x = 0.0
            cmd.angular.z = self.turn()
            self.bot_linear_speed = 0.0
        
        self.get_logger().info(f'err_dist:{self.error_distance:.4f}, err_theta: {self.error_theta*(180/3.14):.2f}, state: {self.state}')
        #self.get_logger().info(f'sped-> lin: {self.move_forward():.2f}, ang: {self.turn():.2f}')
        
        self.publisher_.publish(cmd)
    
    def path_planning(self):
        if(self.state == "Idle"):
            self.final_x += math.cos(self.current_theta)*self.side_length
            self.final_y += math.sin(self.current_theta)*self.side_length
            self.final_theta += self.angle

        #self.get_logger().info(f'Curr-> x: {self.current_x:.2f}, y: {self.current_y:.2f}, cur_theta: {self.current_theta*(180/3.14):.2f}')
        #self.get_logger().info(f'Next-> x: {self.final_x:.2f}, y: {self.final_y:.2f}, nex_theta: {self.final_theta*(180/3.14):.2f}')
        #self.get_logger().info(f'sped-> lin: {self.move_forward():.2f}, ang: {self.turn():.2f}')
        

    #theta corrector when it goes after +180 it starts to calculate the angle in the CW direction from +ve X-axis
    def theta_corrector(self):
        if(self.current_theta < 0 and self.current_theta >= -(math.pi)):            
            self.current_theta += math.pi*2

        if(self.final_theta > 2*math.pi):
            self.final_theta -= 2*math.pi
    
    def move_forward(self):
        #Linear stopping distance calculation based on current speed and decelarating ability
        self.stop_distance = ((self.current_linear_velocity)**2)/(2*self.deccel)

        #Linear Velocity Calculation
        if(self.current_linear_velocity <= self.max_linear_speed and self.error_distance > self.stop_distance):
            #Increasing linear speed if error_distance is greater than stopping_distance
            self.bot_linear_speed += self.accel

        elif(self.error_distance < self.stop_distance):
            #Decreasing speed when error becomes less than stopping distance
            self.bot_linear_speed -= (self.deccel*self.Kp)
        
        return min(self.bot_linear_speed, self.max_linear_speed)

    def turn(self):
        #Angular stopping distance calculation based on current speed and decelarating ability
        self.stop_angle = ((self.current_angular_velocity)**2)/(2*self.d_turn)

        #Angular Velocity Calculation
        if(self.current_angular_velocity <= self.max_angular_speed and self.error_theta > self.stop_angle):
            #Increasing speed if error is greater than stopping angle
            self.bot_angular_speed += self.a_turn

        elif(self.error_theta < self.stop_angle):
            #Decreasing speed when error becomes less than stopping angle
            self.bot_angular_speed -= (self.d_turn*self.turn_Kp)

        return min(self.bot_angular_speed, self.max_angular_speed)
        


def main(args=None):
    rclpy.init(args=args)
    node = ShapeDrawer() # MODIFY NAME
    rclpy.spin(node)
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()