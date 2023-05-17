.. proofpoint_itm documentation master file, created by
   sphinx-quickstart on Tue May 16 19:25:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to proofpoint_itm's documentation!
==========================================

proofpoint_itm is a python package that allows you to interact with the Proofpoint ITM SaaS API.


Installation
============

To install proofpoint_itm, use pip:

.. code-block:: console

   $ pip install proofpoint_itm


Usage
=====

Create a client instance and use it to interact with the API:

.. code-block:: python

   from proofpoint_itm import ITMClient

   itm_client = ITMClient({
         'tenant_id': 'your_tenant_id
         'client_id': 'your_client_id',
         'client_secret': 'your_client_secret'
      })
   
   rules = itm_client.get_rules()

   for rule in rules:
      print(rule['id'])


.. toctree::
   :maxdepth: 1
   :caption: Reference Info:

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
