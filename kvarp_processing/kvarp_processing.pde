import processing.net.*; 
import java.util.*;

// Simple demo of sending commands to RoboDK via the kvar_server.py program

// Make sure that the RoboDK scene is set up according to the documentation in
// kvar_server.py and then ensure that kvar_server.py is running before
// launching this sketch.

Client robotClient;

float CANVAS_WIDTH = 1524;
float CANVAS_HEIGHT = 915;

float lastX = 0;
float lastY = 0;

PImage image;

void settings() {
  size((int)CANVAS_WIDTH, (int)CANVAS_HEIGHT);
}

void setup() {
  // Connect to kvarp_server.py over TCP
  robotClient = new Client(this, "127.0.0.1", 1337);
  background(255);
}

void draw() {}

// Map robot X coordinate to screen coordinate
float mapX(float robotX) {
  return map(robotX, -CANVAS_WIDTH / 2, CANVAS_WIDTH / 2, 0, width);
}

// Map robot Y coordinate to screen coordinate
float mapY(float robotY) {
  return map(robotY, -CANVAS_WIDTH / 2, CANVAS_WIDTH / 2, 0, height);
}

void drawPolyLine(Vector<PVector> pts) {
  float lastX = pts.get(0).x;
  float lastY = pts.get(0).y;
  
  for (PVector pt: pts) {
    robotClient.write("polyline," + lastX + "," + lastY + "," + pt.x + "," + pt.y + "\n");
    line(mapX(lastX), mapY(lastY), mapX(pt.x), mapY(pt.y));
    lastX = pt.x;
    lastY = pt.y;
  }
  
  robotClient.write("nop\n");
}

void drawPoint(float x, float y) {
  robotClient.write("point," + x + "," + y + "\n");

  noStroke();
  fill(0);
  ellipseMode(CENTER);
  ellipse(mapX(lastX), mapY(lastY), 4, 4);
}

void drawLine(float x1, float y1, float x2, float y2) {
  robotClient.write("line," + x1 + "," + y1 + "," + x2 + "," + y2 + "\n");
  
  stroke(0);
  line(mapX(x1), mapY(y1), mapX(x2), mapY(y2));
}

boolean havePrevious = false;
void mousePressed() {
  float x = map(mouseX, 0, width, -CANVAS_WIDTH / 2, CANVAS_WIDTH / 2);
  float y = map(mouseY, 0, height, -CANVAS_HEIGHT / 2, CANVAS_HEIGHT / 2);
  
  if (havePrevious) {
    drawLine(lastX, lastY, x, y);
  } else {
    havePrevious = true;
  }
  
  lastX = x;
  lastY = y;
}
