.. Nalu documentation master file, created by
   sphinx-quickstart on Tue Mar  6 13:48:19 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Nalu: natural language understanding
====================================

Natural language understanding module for English and Dutch.




The Dutch thesaurus is obtained from [OpenTaalBank](http://data.opentaal.org/opentaalbank/thesaurus/).

[UDPipe user manual](https://ufal.mff.cuni.cz/udpipe/users-manual#run_udpipe_input)

A lot of [good stuff](https://github.com/bnosac) comes from the Belgian BMOSAC company's open source efforts you can find on Github. Their [R-package wrapping UDPipe](https://github.com/bnosac/udpipe) in particular replaces the ugly Frog machine.
The Python binding to UDPipe is a thin wrapper around the C++ interface and makes it difficult to figure out how to use it. Some info [is available here](https://github.com/ufal/udpipe/tree/master/bindings/python/examples) but see the code is something like this


.. toctree::
   :maxdepth: 2
   :caption: Contents:
.. automodule:: nalu
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
