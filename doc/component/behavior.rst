.. _Behavior:

Behavior
========

The behavior class contains such things as runnables and events.

.. py:class:: InternalBehavior(name : str,componentRef : str,multipleInstance=False,parent=None)

   Constructor.

Methods
-------

.. py:method:: InternalBehavior.createRunnable(name : str,invokeConcurrently=False,symbol=None, portAccess=None)
   
   Creates a new runnable and inserts it to the intenal list of runnables.
   
   symbol can be used to override the default symbol name (default is to set symbol = name of runnable).
   
   portAccess must be a list (or other kind of iterable) of port names or data element references.