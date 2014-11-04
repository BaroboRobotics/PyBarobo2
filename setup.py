#!/usr/bin/env python3
import tempfile
import subprocess
import os
import shutil
#from distutils.core import setup,Extension
#from distutils.command.build_py import build_py
import setuptools
from setuptools import setup, Extension
import platform
import sys

origCWD = os.getcwd()
projDir = os.path.dirname(origCWD)
#projDir = os.path.join(os.path.dirname(origCWD), 'BaroboBrowser')
buildDir = os.path.join(origCWD, 'build-ext-'+ platform.platform())

try:
    if not os.path.isdir(buildDir):
        os.mkdir(buildDir)
except Exception as e:
    print('Could not create build directory:')
    print(buildDir)
    print('Aborting build...')
    sys.exit(0)

# Go to the build directory
os.chdir(buildDir)

if platform.system() == 'Windows':
    # Build our C/C++ library into our tempdir staging directory
    if not os.path.exists(os.path.join(buildDir, 'Makefile')):
        subprocess.check_call([
                'cmake', 
                '-G', 'MinGW Makefiles', 
                '-DCMAKE_CXX_FLAGS=-fPIC', 
                '-DBUILD_SHARED_LIBS=OFF',
                '-DCMAKE_BUILD_TYPE=Debug',
                projDir])
    subprocess.check_call(['mingw32-make', 'baromesh', 'VERBOSE=1'])
    libraries=[ 'baromesh',
                'sfp', 
                'rpc',
                'robot-interface',
                'dongle-interface',
                'boost_log-mgw48-mt-d-1_56',
                'boost_thread-mgw48-mt-d-1_56',
                'boost_system-mgw48-mt-d-1_56',
                'ws2_32',
                'setupapi']
else:
    # Build our C/C++ library into our tempdir staging directory
    if not os.path.exists(os.path.join(buildDir, 'Makefile')):
        subprocess.check_call([
                'cmake', 
                '-G', 'Unix Makefiles', 
                '-DCMAKE_CXX_FLAGS=-fPIC', 
                '-DBUILD_SHARED_LIBS=OFF',
                '-DCMAKE_BUILD_TYPE=Debug',
                projDir])
    subprocess.check_call(['make', 'baromesh', 'VERBOSE=1'])
    libraries=[ 'baromesh',
                'sfp', 
                'rpc',
                'robot-interface',
                'dongle-interface',
                'boost_log',
                'boost_thread',
                'boost_system']

#Go back to our original directory
os.chdir(origCWD)

if os.environ['BOOST_ROOT'] is None:
    print('Environment variable BOOST_ROOT is not declared. aborting...')
    sys.exit(0)

try:
    setup(name='PyBarobo2',
        version='2.0.0',
        description='Barobo Linkbot module',
        author='David Ko',
        author_email='david@barobo.com',
        url='http://www.barobo.com',
        packages=['demo'],
        ext_package='linkbot',
        ext_modules=[Extension('__linkbot', 
          sources=['_linkbot.i'],
          swig_opts=['-threads', '-c++'],
          include_dirs=[
            os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh', 'include'),
            os.path.join(origCWD, 'PyLinkbotWrapper', 'src'),
            ],
          library_dirs=[
            os.path.join(buildDir, 'BaroboBrowser','qlinkbot','baromesh'),
            os.path.join(buildDir, 'BaroboBrowser','qlinkbot','libsfp'),
            os.path.join(buildDir, 'BaroboBrowser','qlinkbot','ribbon-bridge'),
            os.path.join(buildDir, 'BaroboBrowser','qlinkbot','ribbon-bridge-interfaces'),
            os.path.join(os.environ['BOOST_ROOT'], 'stage', 'lib'),
            buildDir],
          libraries=libraries,
          )],
        package_dir={'linkbot':''},
        py_modules=['linkbot._linkbot'],
        zip_safe = False,
        )
except Exception as e:
    print(e)

