

.. image:: https://codecov.io/gh/conanfanli/slotomania/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/conanfanli/slotomania
   :alt: codecov


.. image:: https://pyup.io/repos/github/conanfanli/slotomania/shield.svg
   :target: https://pyup.io/repos/github/conanfanli/slotomania/shield.svg
   :alt: pyup


Slotomania
==========

A code generator that transforms schemas to Python slot classes and typescript interfaces

Vocabulary
==========

slots
-----

Refer to Python slot classes. They're just like regular classes with ``__slots__`` defined.

Sloto
-----

A base class defined in `slotomania/core.py <./slotomania.core.py>`_.
Provides two methods: ``sloto_to_dict()`` which converts the instance to a dictionary, and ``__repr__`` for debugging purpose.

actions or redux actions
------------------------

Redux actions or action creators: see https://redux.js.org/basics/actions

Examples
========

.. code-block:: Python

   from slotomania.contrib.marshmallow_converter import (
       schemas_to_slots,
   )
   class Eye(Schema):
       color = fields.String(required=True)


   class Head(Schema):
       hair = fields.String(requried=True)


   class Body(Schema):
       eyes = fields.List(fields.Nested(Eye()), required=True)
       mouth = fields.Decimal(required=True)
       poo = fields.Float(required=True)
       foot = fields.DateTime(required=True)
       head = fields.Nested(Head(), required=True)

   assert format_python_code(schemas_to_slots([
       Eye(),
       Head(),
       Body(),
   ])) == format_python_code("""
   from slotomania.core import Sloto
   import datetime
   import decimal
   import typing

   class Eye(Sloto):
       __slots__ = ['color']
       def __init__(
           self,
           color: str,
       ) -> None:

           self.color = color


   class Head(Sloto):
       __slots__ = ['hair']
       def __init__(
           self,
           hair: str = None,
       ) -> None:

           self.hair = hair


   class Body(Sloto):
       __slots__ = ['eyes', 'foot', 'head', 'mouth', 'poo']
       def __init__(
           self,
           eyes: typing.List[Eye],
           foot: datetime.datetime,
           head: Head,
           mouth: decimal.Decimal,
           poo: float,
       ) -> None:

           self.eyes = eyes
           self.foot = foot
           self.head = head
           self.mouth = mouth
           self.poo = poo
           """
           )

Setup for development
=====================


* Run ``make setup`` this will create git pre-commit hooks that converts this markdown to reStructured text which is needed for PyPI
* Install packages in `dev-requirements.txt <./dev-requirements.txt>`_
