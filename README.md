  
**Step 1 -** Download the vritual gamepad driver.  
Under the hood, ```vgamepad``` uses the [ViGEm](https://github.com/ViGEm) C++ framework, for which it essentially provides python bindings and a user-friendly interface.
Thus far, ```vgamepad``` is compatible with Windows only.

**Step 2 -**: Download sensor server in android from this [link](https://github.com/umer0586/SensorServer) and start the server, copy the ip address and port.

Note: let me know if their is similar app exist for ios.

**Step 3 -** update ip and port that you copied from android
![](file:///E:/Downloads/WhatsApp%20Image%202023-10-17%20at%2009.22.51_ecd80f3c.jpg)

**Step 4 -** Run command
```cmd
    python xbox-sensor.py
```

Taadaaaa! you have brand new controller, but its virtual.

![](file:///E:/Downloads/giphy.gif)