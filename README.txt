PyLinkbot
=========

PyLinkbot - A Python package for controlling Barobo Linkbots
Contact: David Ko <david@barobo.com>

Linkbots are small modular robots designed to play an interactive role in
computer science and mathematics curricula. More information may be found at
http://www.barobo.com .

Requirements
------------

This package is built against Python 3.4 . Python 2 is explicitely not
supported, and other versions of Python 3 may or may not work. Additionally,
the SciPy <http://www.scipy.org> is highly recommended for graphical plotting
and more.

Installation
------------

The recommended way to install this package is through setuptools utilities,
such as "easy_install" or "pip". For example:

    easy_install3 PyLinkbot

or

    pip3 install PyLinkbot

Building
--------

As of version 2.3.2, building from the setup.py script has been tested on Ubuntu
14.04 LTS. The requirements to build this package are:

    cmake
    git
    python3-dev
    gcc
    g++

To install all of these at once, run the command:

    sudo apt-get install cmake git python3-dev gcc g++

Next, you should be able to run the setup script.

    python3 setup.py build

The script will download and build all necessary dependencies, including Boost
and the Linkbot Labs SDK package. Please note that the building process can take
quite a bit of time to complete, and there is currently minimal UI feedback
during the process, so patience is appreciated. 
