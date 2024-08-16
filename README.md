# GPDL Latency tester
**What is GPDL Tester?**  
GPDL Tester is a tool for measuring latency of gamepad buttons and joysticks. It helps to determine how long it takes from pressing a button or moving a stick on the gamepad to registering this action on the PC. This allows gamers to check the performance of their gamepad and make sure it is working optimally for their games.  

**How GPDL works**  
1. The device presses the button (or deflects the stick) of the gamepad using the two pins connected to it.
3. The gamepad sends an action signal to the PC.
4. The program receives a signal about pressing the button (or rejecting the stick) from the gamepad.
5. The program calculates the time difference between the action (step 1) and the received signal (step 3).
6. The cycle performs 2000 tests to obtain accurate results.

![image](https://github.com/user-attachments/assets/2f5dc737-cd30-4101-bacd-b26d53251c3e)

**Preparing for testing**  
1. Disassemble the gamepad to access the pins of its stіck or buttons.
2. Connect the two GPDL tester leads to the pins.
3. Turn on the gamepad and connect it to the computer via Bluetooth, cable, or receiver.
4. Connect the GPDL device to the computer.
5. Run the program "GPDL.exe".
6. Follow the instructions in the middle of the program.
7. Wait for the test to complete.

![image](https://github.com/cakama3a/GPDL/assets/15096106/7b21cc91-586f-4afc-82be-c4194e565790)  

**Receiving the results**  
After the test is completed, the results will be displayed on the gamepadla.com website in the form of a graph. All test data is saved in a separate text file in the program folder. You can also publish the results on gamepadla.com for public access.  

**Program interface**  
![image](https://github.com/cakama3a/GPDL/assets/15096106/f36c402c-d134-44ec-a0d6-25c60e4cc688)

## How to create a GPDL device yourself
**Required components**
1. Arduino Nano - https://amzn.to/3tSbvB3 | https://s.click.aliexpress.com/e/_DczmEt1
2. Cable - https://s.click.aliexpress.com/e/_DlX7bmn | https://amzn.to/3MaUU1F
3. Case STL - https://www.thingiverse.com/thing:6283094
4. Resistors kit - https://s.click.aliexpress.com/e/_DlKKEy3
5. Soldering iron - https://s.click.aliexpress.com/e/_Debb6R5
   
**Optional components**  
1. Gecko tape - https://s.click.aliexpress.com/e/_DegtRf1
2. Conductive tape - https://amzn.to/43b0x7m
3. Crocodile type Clip - https://s.click.aliexpress.com/e/_DEfqkmT
4. Cable Sleeve 2mm - https://s.click.aliexpress.com/e/_DBg9qhZ
5. Heat Shrink Tube - https://s.click.aliexpress.com/e/_DkOt667

## Actual scheme
The current GPDL tester scheme for version 2.2.5 and higher. The diagram shows an Arduino Micro, because I couldn't find a picture of a Nano. View the diagram in a more professional [Chart format](https://wokwi.com/projects/404185236840396801)  
![image](https://github.com/user-attachments/assets/a04ac64a-1dc5-4e2e-bec9-8d100f0c104b)  

## Required software
[Download GPDL program](https://github.com/cakama3a/GPDL/tree/StickTest/dist) for Windows 10/11  
[Arduino code](https://github.com/cakama3a/GPDL/blob/StickTest/Arduino.ino) this code should be flashed to the Arduino via [Arduino IDE](https://www.arduino.cc/en/software/)  

## Video tutorial
**Currently outdated (but still useful)**  
[Video tutorial](https://www.youtube.com/watch?v=epm2li1hrK8), the Arduino circuit in the video is a bit outdated, but the principle is the same  


## ⚠️WARNING:
1. The author cannot guarantee that the gamepad will not malfunction, so do all tests at your own risk!  
2. The joystick testing mode is still experimental and may require additional resistors on the contacts depending on the stick voltage  

**LINKS:**  
Donate: https://ko-fi.com/gamepadla  
A website with a catalog of tested gamepads: https://gamepadla.com  
