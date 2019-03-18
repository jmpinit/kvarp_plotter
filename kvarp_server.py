import sys
import os
import socket
import collections
import time
import threading
from random import randint
import robolink
import robodk as rdk

# A server which controls a Kuka KR 16 industrial robot arm via RoboDK based on
# simple plotting/drawing commands. For example:

# "line,100,50,200,250\n" causes the robot to move to a position above the
# drawing surface (distance set by DRAW_OFFSET), approach the surface, move
# from (100, 50) to (200, 250), and then lift back to the offset distance

# To tell the robot where the drawing surface is there must be a coordinate
# frame in the RoboDK scene called "Frame draw". The robot must have a tool
# named "Tool" that matches the orientation & offset of the real plotting tool.

TCP_IP = '127.0.0.1'
TCP_PORT = 1337

DRAW_OFFSET = 30
DRAW_ACCELERATION = 5000
DRAW_SPEED = 300

# Draw commands are submitted by clients and executed on the robot
draw_commands = collections.deque()

class RobotArtist(object):
    def __init__(self, run_on_real=False, offset=30, acceleration=1000, speed=500):
        self.offset = offset

        self.robodk = robolink.Robolink() # Link with simulator
        self.robot = self.robodk.Item('KUKA KR 16 2')
        self.draw_frame = self.robodk.Item('Frame draw')
        self.draw_tool = self.robodk.Item('Tool')

        self.robot.setAcceleration(acceleration)
        self.robot.setSpeed(speed)

        if run_on_real:
            self.connect_to_real_robot()

    def connect_to_real_robot(self):
        if self.robodk.RunMode() != robolink.RUNMODE_SIMULATE:
            raise Exception('Cannot run on robot outside of simulation mode')

        # Connect to the robot using default IP
        self.robot.Connect() # Try to connect once
        status, status_msg = self.robot.ConnectedState()

        if status != robolink.ROBOTCOM_READY:
            # Stop if the connection did not succeed
            print(status_msg)
            raise Exception("Failed to connect: " + status_msg)

        # This will set to run the API programs on the robot and the simulator
        # (online programming)
        self.robodk.setRunMode(robolink.RUNMODE_RUN_ROBOT)

    def move_pen_to(self, x, y, z):
        self.robot.setPoseFrame(self.draw_frame)
        self.robot.setPoseTool(self.draw_tool)

        orient_frame2tool = self.draw_tool.Pose()
        orient_frame2tool[0:3, 3] = rdk.Mat([0, 0, 0])

        pos = rdk.transl(x, y, z) * orient_frame2tool

        self.robot.MoveL(pos)

    def draw_point(self, x, y):
        print('Point at ({}, {})'.format(x, y))
        self.move_pen_to(x, y, -self.offset)
        self.move_pen_to(x, y, 0)
        self.move_pen_to(x, y, -self.offset)

    def draw_line(self, x1, y1, x2, y2):
        print('Line from ({}, {}) to ({}, {})'.format(x1, y1, x2, y2))
        self.move_pen_to(x1, y1, -self.offset)
        self.move_pen_to(x1, y1, 0)
        self.move_pen_to(x2, y2, 0)
        self.move_pen_to(x2, y2, -self.offset)

    def draw_polyline(self, lines):
        print('Poly line of {} lines'.format(len(lines)))
        x0, y0 = lines[0][0]
        self.move_pen_to(x0, y0, -self.offset)

        for line in lines:
            x2, y2 = line[1]
            self.move_pen_to(x2, y2, 0)

        xLast, yLast = lines[-1][1]
        self.move_pen_to(xLast, yLast, -self.offset)

def handle_message(message):
    parts = message.split(',')
    cmd = parts[0]
    params = parts[1:]

    if cmd == 'nop':
        # Convenient for ending polylines without side effects
        draw_commands.append(('nop'))
    elif cmd == 'point':
        x, y = [float(v) for v in params]
        draw_commands.append(('point', x, y))
    elif cmd == 'line':
        x1, y1, x2, y2 = [float(v) for v in params]
        draw_commands.append(('line', x1, y1, x2, y2))
    elif cmd == 'polyline':
        # Multiple polyline commands will be collapsed into a single command
        # as long as they are grouped together before any other command
        x1, y1, x2, y2 = [float(v) for v in params]
        draw_commands.append(('polyline', x1, y1, x2, y2))
    else:
        print('Unrecognized command: "{}"'.format(message))

def server():
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind((TCP_IP, TCP_PORT))
    serverSock.listen(1)

    print('Server started')

    while True:
        conn, addr = serverSock.accept()
        print('Accepted connection from client at {}'.format(addr))

        buffer = ''

        while True:
            data = conn.recv(1)

            if not data:
                break

            buffer += data.decode('utf-8')

            if '\n' in buffer:
                end_index = buffer.index('\n')
                message = buffer[:end_index + 1].strip()
                buffer = buffer[end_index + 1:]
                handle_message(message)

        print('Connection to client closed')
        conn.close()

def main():
    global draw_commands

    server_thread = threading.Thread(target=server)
    server_thread.setDaemon(True)
    server_thread.start()

    waldo = RobotArtist(True, DRAW_OFFSET, DRAW_ACCELERATION, DRAW_SPEED)

    while True:
        if len(draw_commands) > 0:
            next_command = draw_commands.popleft()

            command_type = next_command[0]

            if command_type == 'point':
                _, x, y = next_command
                waldo.draw_point(x, y)
            elif command_type == 'line':
                _, x1, y1, x2, y2 = next_command
                waldo.draw_line(x1, y1, x2, y2)
            elif command_type == 'polyline':
                polyline = []

                while True:
                    while len(draw_commands) == 0:
                        time.sleep(1/1000)

                    next_command = draw_commands.popleft()
                    command_type = next_command[0]

                    if not command_type == 'polyline':
                        break

                    _, x1, y1, x2, y2 = next_command
                    polyline += [[[x1, y1], [x2, y2]]]

                waldo.draw_polyline(polyline)
            else:
                # Don't run unknown commands or nop
                pass
        else:
            time.sleep(1/1000)

main()
