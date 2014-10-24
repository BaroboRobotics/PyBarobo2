#!/usr/bin/env python3
import tempfile
import subprocess
import os
import shutil
#from distutils.core import setup,Extension
#from distutils.command.build_py import build_py
import setuptools
from setuptools import setup, Extension

origCWD = os.getcwd()
#projDir = os.path.dirname(origCWD)
projDir = os.path.join(origCWD, 'PyLinkbotWrapper')
# Create a temporary build directory
tempdir = tempfile.mkdtemp()
# Go to that directory
os.chdir(tempdir)
# Build our C/C++ library into our tempdir staging directory
subprocess.check_call([
        'cmake', 
        '-G', 'Unix Makefiles', 
        '-DCMAKE_CXX_FLAGS=-fPIC', 
        '-DBUILD_SHARED_LIBS=OFF',
        '-DCMAKE_BUILD_TYPE=Debug',
        projDir])
subprocess.check_call(['make', 'VERBOSE=1'])

#Go back to our original directory
os.chdir(origCWD)

#dist = setup(name='CppTestLib',
try:
    setup(name='PyBarobo2',
        version='2.0.0',
        description='Barobo Linkbot module',
        author='David Ko',
        author_email='david@barobo.com',
        url='http://www.barobo.com',
        #packages=['barobo'],
        ext_package='linkbot',
        ext_modules=[Extension('_linkbot', 
          sources=['linkbot.i'],
          swig_opts=['-c++'],
          include_dirs=[
            os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh', 'include'),
            os.path.join(origCWD, 'PyLinkbotWrapper', 'src'),
            ],
          library_dirs=[
            os.path.join(tempdir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','baromesh'),
            os.path.join(tempdir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','libsfp'),
            os.path.join(tempdir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','ribbon-bridge'),
            os.path.join(tempdir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','ribbon-bridge-interfaces'),
            os.path.join(os.environ['HOME'], '.local', 'lib'),
            tempdir],
          libraries=[ 'baromesh', 
                      'linkbot_wrapper', 
                      'sfp', 
                      'rpc',
                      'robot-interface',
                      'dongle-interface',
                      'boost_log',
                      'boost_thread',
                      'boost_system'],
          )],
        package_dir={'linkbot':''},
        py_modules=['linkbot._linkbot', 'linkbot.linkbot']
        )
except Exception as e:
    print(e)

#build_py = build_py(dist)
#build_py.ensure_finalized()
#build_py.run()

# Unlink temp directory
shutil.rmtree(tempdir)
