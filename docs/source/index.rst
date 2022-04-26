===================
Aerosense Dashboard
===================

``aerosense-dashboard`` is a data dashboard allowing high-level visualisation of data from the aerosense system.

 - The ``data-gateway`` library is responsible for the data collection and ingress to GretaDB and GretaStore. 
 - The ``aerosense-tools`` library can access and manipulate data from GretaDB or the GretaStore by any python client.

This dashboard uses a combination of its own code and ``aerosense-tools`` to access and visualise data from GretaDB.

.. NOTE::
  Data from GretaStore is not visualised because it's high frequency acoustic data, unsuited to dashboarding.



Contents
========

.. toctree::
   :maxdepth: 2

   using_the_dashboard
   developing_the_dashboard
   deploying_the_dashboard
   authentication
