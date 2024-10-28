# Demo System Example

This folder contains an example which demonstrates how the template mechanism is intended to be used.

## Software layers

This example uses 3 layers. At the bottom we have the Python AUTOSAR XML API (This git repo).
The [Factory](factory.py) layer enables an easy way to create commonly used elements such as data types and port-interfaces.
It acts like an abstraction layer, hiding most of the low-level details seen in the Python AUTOSAR XML API.

1. Template element layer
2. Factory layer
3. Python AUTOSAR XML layer

## components

The file [component.py](component.py) contains 3 example SWCs:

- ReceiverComponent (ApplicationSoftwareComponentType)
- TimerComponent (ApplicationSoftwareComponentType)
- CompositionComponent (CompositionSwComponentType)

The composition "CompositionComponent" wraps the two application SWCs and create some connectors between them.
The component TimerComponent provides a timer API (Client-server-interface) that the ReceiverComponent uses.
