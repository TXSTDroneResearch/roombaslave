# Roomba Scripts

These scripts were used to retrieve statistics about the Roomba, which vary script-to-script.

## fwd_150.py

This script (while untested) is supposed to spin the Roomba until its battery reaches 75%, then commands it to move forward exactly 1.5 meters. This was used to test the **accuracy of the Roomba**'s move commands.

## rot_90.py

This script uses the MPU-9255 IMU to attempt an accurate 90 degree rotation. The meat of the code is in `TurnRobot`. The gist of it is:
* We begin a (counter)clockwise turn until it reaches the target angle, then we issue a stop command.
* If it turns out the Roomba overshot the target angle, we begin a turn in the opposite direction until we hit the target.
* Rinse and repeat until we're within a certain threshold `precision`.