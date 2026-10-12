# TelescopeBot Vision & Compute Architecture

## Core Requirements
The head/chest of TelescopeBot needs to house the Jetson compute unit and the Intel RealSense camera. 
Since the spine is telescoping, this upper section (the "Chest Box") will move vertically by up to 25cm.

## Power Routing
- **Problem:** Powering a Jetson and RealSense requires significant stable current (usually 5V/4A minimum). If the battery is in the Waist Box (to keep center of gravity low), we must route power UP the telescoping spine.
- **Solution:** Use a coiled or flexible silicone wire harness running parallel to the threaded rod. The continuous rotation of the lead screw must not entangle the wire harness. 
- **Recommendation:** Place a small buck converter (12V to 5V) *inside* the Chest Box. Route 12V from the main battery up the spine. 12V transmission suffers less voltage drop over flexible wiring than 5V.

## RealSense Mounting (The "Head")
- **Placement:** The RealSense should be mounted at the very top of the Chest Box, potentially on a 2-DOF pan/tilt bracket using 2x MG996R servos.
- **Why Pan/Tilt?** The field of view is critical. When the spine extends to 100cm, the robot will need to pitch the camera down to see its own hands manipulating a table or doorknob.

## Jetson Mounting
- **Orientation:** Mount the Jetson vertically inside the Chest Box.
- **Cooling:** The Jetson Orin/Nano gets hot under RL workloads. Ensure the 3D printed Chest Box has exhaust vents and a dedicated 40mm fan drawing air across the heatsink.

## Next Steps for CAD
When designing the Chest Box in CAD:
1. Include standard M3 mounting standoffs for the Jetson carrier board.
2. Include a cutout and M3 mounts for the RealSense (most RealSense models have two M3 threaded holes on the back).
3. Ensure cable strain relief points for the USB-C cable connecting the RealSense to the Jetson.
