SteeringWheelFeedback
=====================

Let's assume we have a Steering Wheel Switch (SWS) with push buttons. These push buttons can be used for things such as:

- Controlling the radio/media functions of the vehicle.
- Navigating through menu systems in the instrument cluster display.

Our first goal of this tutorial will be to model an AUTOSAR component called SteeringWheelButtonFeedback. This component will be responsible for detecting the
button pushes and sending their statuses as AUTOSAR signals to other components.

+------------------------+------------------------------+
| Physical Button        | Corresponding AUTOSAR signal |
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
