# Feasibility Study: Mid-Sized 3D Printed Humanoid

## 1. The Vision
- **Goal:** A humanoid robot capable of reaching doorknobs and tables (~90-110cm tall, the size of a 5-6 year old).
- **Manufacturing:** 3D printed (PLA/PETG), utilizing hollow structures to drastically reduce weight compared to metal frames.
- **Control:** Robust, AI-driven control (Jetson compute + RealSense depth).
- **Cost:** Cheap, utilizing on-hand harvested parts.

## 2. On-Hand Inventory Analysis

### Compute & Vision (Excellent)
- **Compute:** Jetson (Nano/Orin), Raspberry Pi. (This is *perfect* for running modern RL policies, kinematics, and Gemini/VLM integration).
- **Vision:** Intel RealSense, standard RGB cameras. (RealSense is the gold standard for robotic spatial awareness).

### Actuators (The Limiting Factor)
- **2x DS5160 SSG (60 kg-cm):** Extremely strong standard servos.
- **22x TowerPro MG996R (~10 kg-cm):** The classic workhorse servo. You have enough for a full humanoid (usually requires ~16-20 DOF).
- **4x Waveshare SC15 (17 kg-cm):** Serial bus servos.
- **1x Waveshare ST3215 (30 kg-cm):** Serial bus servo.
- **6x Fiiec FS5103R (~3 kg-cm):** Likely continuous rotation or standard low-torque.
- **4x MG90s (~2 kg-cm):** Micro servos, good for a head/neck pan-tilt or small hands.

## 3. The Physics Check (The Torque Problem)

While 3D printing PLA/PETG hollow will save a massive amount of weight, the laws of leverage still apply. 

If the robot is ~100cm tall, its leg segments (thigh and calf) will be roughly **25cm** each.
Let's assume an aggressively optimized hollow 3D-printed body weighing only **4 kg** total.

If the robot bends its knees in a walking stance, a single knee might need to support the weight of the upper body (~3 kg).
* **Torque = Force × Distance**
* **Knee Torque = 3 kg × 25 cm = 75 kg-cm** (static holding torque)
* Dynamic walking requires even more torque (often 1.5x to 2x the static load).

**Conclusion on Direct Drive:** Your strongest servos are 60 kg-cm (x2). The MG996Rs are 10 kg-cm. Directly attaching these to the joints of a 100cm tall robot will result in the robot collapsing under its own weight, even if printed as lightly as possible.

## 4. Engineering Solutions

To achieve your goal with the hardware on hand, we need to cheat physics using clever 3D printing and design. Here are three viable paths:

### Path A: The Clever Mechanical Humanoid
Since you have a 3D printer, we don't have to do direct-drive!
- **Dual Servos:** You have 22 MG996Rs. You can design 3D-printed brackets that pair two servos together for joints like the knee and hip, doubling the torque (20 kg-cm).
- **Gravity Compensation (Springs/Bungees):** We can design the 3D printed legs to incorporate surgical tubing or extension springs acting as artificial "muscles" in parallel with the servos. The springs support the robot's static weight, meaning the servos only have to exert force to *move*, not to hold the robot up.
- **Cycloidal/Planetary Gearboxes:** Print 3:1 or 4:1 gearboxes for the MG996Rs for the high-torque joints.

### Path B: The "Mobile Manipulator" (Highly Recommended)
If the primary goal is reaching doorknobs and interacting with tables:
- Build a differential-drive wheeled base (using the FS5103R continuous servos, or borrow motors from ROSPug).
- Build a 100cm tall spine and torso on top of the base.
- Use the MG996Rs to build two 5-6 DOF arms. Arms require drastically less torque than legs (a 30cm arm holding 0.5kg only needs ~15 kg-cm at the shoulder, which is manageable).
- *Pros:* Extremely robust, easy to train, won't fall over, solves the leg torque problem entirely.

### Path C: Scale Down to a "Toddler"
- Scale the height down to ~50-60cm (size of a 1-2 year old).
- At this scale, leg segments are ~12cm. A 2.5kg robot needs `2.5kg * 12cm = 30 kg-cm` at the knee. 
- You can use the 60 kg-cm servos for the knees, the 30 kg-cm and 17 kg-cm for the hips, and the MG996Rs for the arms/ankles. This matches your inventory almost perfectly.

## 5. Next Steps

Which path excites you the most? 
1. We design a 100cm humanoid utilizing 3D-printed gearboxes/springs.
2. We design a tall wheeled robot with humanoid arms.
3. We build a smaller ~60cm toddler-sized humanoid that perfectly matches your servo inventory.

Let me know, and we can start laying out the CAD architecture!
