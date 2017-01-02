:mod:`autosar.behavior` --- Component Behavior
==============================================

.. _InternalBehavior:

InternalBehavior
----------------

   The InternalBehavior class contains runnables, events and other parts for describing the behavior of an associated AUTOSAR component type

Constructor
~~~~~~~~~~~

.. py:class:: InternalBehavior(name : str, componentRef : str, multipleInstance=False, parent=None)

Attributes
~~~~~~~~~~

   .. py:attribute:: InternalBehavior.name
      
      The name of the object as a string.
        
   .. py:attribute:: InternalBehavior.ref
         
      (readonly) reference to the object as a string.
   
   .. py:attribute:: InternalBehavior.runnables
   
      list of runnables
      
   .. py:attribute:: InternalBehavior.events
   
      list of events


Methods
~~~~~~~

.. py:method:: InternalBehavior.createRunnable(name : str, invokeConcurrently=False, symbol=None, portAccess=None)
   
   Creates a new runnable and inserts it to the intenal list of runnables.
   
   symbol can be used to override the default symbol name (default rule is to set symbol to the name of runnable).
   
   portAccess must be a list (or other kind of iterable) of port names or data element references.