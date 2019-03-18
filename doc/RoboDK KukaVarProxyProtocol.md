# RoboDK KukaVarProxy Control Protocol

[RoboDK](http://robodk.com) connects to KUKA robots using
[KukavarProxy](https://github.com/ImtsSrl/KUKAVARPROXY/) to read and write
global variables on the robot. A corresponding script written in KRL must be
running on the robot. The script is supplied with RoboDK and is not open
source, but I have documented the global variable interface below.

## Variables

From [the online RoboDK documentation](https://robodk.com/doc/en/Robots-KUKA.html)
the global variables that must be created on the robot are the following:

```
INT COM_ACTION=0
INT COM_ACTCNT=0
REAL COM_ROUNDM=0
REAL COM_VALUE1=0
REAL COM_VALUE2=0
REAL COM_VALUE3=0
REAL COM_VALUE4=0
DECL E6AXIS COM_E6AXIS
DECL FRAME COM_FRAME
DECL POS COM_POS
```

Global variables can be defined on the Kuka Robot Controller in the file
**KRC\R1\STEU\$config.dat**.

## Commands

Each command is selected by setting COM_ACTION to an integer value.

0/1) NOP
2) Move PTP, to COM_E6AXIS. Approximated if COM_ROUNDM > 0
3) Move LIN, to COM_FRAME. Approximated if COM_ROUNDM > 0
4) Move CIRC, through COM_POS to COM_FRAME. Approximated if COM_ROUNDM > 0
5) Set tool frame to COM_FRAME
6) Set center point velocity to COM_VALUE1
7) Set center point velocity to COM_VALUE1, axis velocities to COM_VALUE2, center point acceleration to COM_VALUE3, and axis accelerations to COM_VALUE4
8) Set approximation percentage to COM_ROUNDM and set advance planning
9) Wait for COM_VALUE1 seconds
10) Set IO of index COM_VALUE1 to true if COM_VALUE2 > 0.5, and false otherwise
11) Axis move to COM_E6AXIS and then linear move to COM_FRAME, then sync planning lookahead
12) Wait for IO of index COM_VALUE1 to become true if COM_VALUE2 > 0.5 and wait for it to turn false otherwise
13) Run custon program of ID COM_VALUE1
