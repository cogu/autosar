Part 1
======

Our first Component
-------------------

In our example vehicle let's assume we have a steering wheel with control buttons. These steering wheel buttons can be used for things such as:
- Controlling the radio/media functions of the vehicle.
- Navigating through menu systems in the instrument cluster display.

Our first goal of this tutorial will be to model an AUTOSAR component called SteeringWheelButtonFeedback. This component that is responsible for listening
to button presses and sending their status as AUTOSAR signals to other components.

+------------------------+------------------------------+
| Physical Button/Switch | Corresponding AUTOSAR signal |
+========================+==============================+
| Up                     | SWS_PushButtonStatus_Up      |
+------------------------+------------------------------+
| Down                   | SWS_PushButtonStatus_Down    |
+------------------------+------------------------------+
| Right                  | SWS_PushButtonStatus_Right   |
+------------------------+------------------------------+
| Left                   | SWS_PushButtonStatus_Left    |
+------------------------+------------------------------+
| Enter                  | SWS_PushButtonStatus_Enter   |
+------------------------+------------------------------+
| Back                   | SWS_PushButtonStatus_Back    |
+------------------------+------------------------------+
| Home                   | SWS_PushButtonStatus_Home    |
+------------------------+------------------------------+
