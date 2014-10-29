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
#projDir = os.path.dirname(origCWD)
projDir = os.path.join(origCWD, 'PyLinkbotWrapper')
buildDir = os.path.join(projDir, 'build-'+platform.platform())

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
    subprocess.check_call(['make', 'linkbot_wrapper', 'VERBOSE=1'])
    libraries=[ 'linkbot_wrapper', 
                'baromesh',
                'sfp', 
                'rpc',
                'robot-interface',
                'dongle-interface',
                'boost_log-mgw48-mt-d-1_56',
                'boost_thread-mgw48-mt-d-1_56',
                'boost_system-mgw48-mt-d-1_56'],
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
    subprocess.check_call(['make', 'linkbot_wrapper', 'VERBOSE=1'])
    libraries=[ 'linkbot_wrapper', 
                'baromesh',
                'sfp', 
                'rpc',
                'robot-interface',
                'dongle-interface',
                'boost_log',
                'boost_thread',
                'boost_system'],

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
          swig_opts=['-threads', '-c++'],
          include_dirs=[
            os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh', 'include'),
            os.path.join(origCWD, 'PyLinkbotWrapper', 'src'),
            ],
          library_dirs=[
            os.path.join(buildDir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','baromesh'),
            os.path.join(buildDir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','libsfp'),
            os.path.join(buildDir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','ribbon-bridge'),
            os.path.join(buildDir, 'LinkbotLabs', 'BaroboBrowser','qlinkbot','ribbon-bridge-interfaces'),
            os.path.join(os.environ['HOME'], '.local', 'lib'),
            buildDir],
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

