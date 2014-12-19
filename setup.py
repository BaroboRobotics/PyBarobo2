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

projDir = os.getcwd()
# projDir = os.path.dirname(origCWD)
# projDir = os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh')
buildDir = os.path.join(projDir, 'build-ext-'+ platform.platform())

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

boost_libs = ['log', 'thread', 'system', 'filesystem', 'python3']

libraries=[ 'baromesh',
            'daemon-interface', 
            'sfp', 
            'rpc',
            'robot-interface',
            'commontypes-proto',
            'rpc-proto' ]

if platform.system() == 'Windows':
    mingw_version='49'
    # Build our C/C++ library into our tempdir staging directory
    if not os.path.exists(os.path.join(buildDir, 'Makefile')):
        subprocess.check_call([
                'cmake', 
                '-G', 'MinGW Makefiles', 
                #'-DCMAKE_CXX_FLAGS=-fPIC -DBOOST_ALL_DYN_LINK', 
                '-DBUILD_SHARED_LIBS=OFF',
                '-DCMAKE_BUILD_TYPE=Debug',
                projDir])
    subprocess.check_call(['mingw32-make', 'VERBOSE=1'])
    libraries+=[ 'msvcr100',
                 'ws2_32',
                 'setupapi']
    boost_libraries = []
    for lib in boost_libs:
        boost_libraries += ['boost_'+lib+'-mgw'+mingw_version+'-mt-1_57']
    libraries += boost_libraries
    data_files = [('linkbot', 
        [ 'dlls/libgcc_s_dw2-1.dll',
          'dlls/libstdc++-6.dll',
          'dlls/libwinpthread-1.dll',
          os.path.join(buildDir, '_linkbot.pyd'), 
          ])]
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
    subprocess.check_call(['make', 'VERBOSE=1'])
    boost_libraries = []
    for lib in boost_libs:
        boost_libraries += ['boost_'+lib]
    libraries += boost_libraries
    data_files = [('linkbot', [os.path.join(buildDir, '_linkbot.so')])]

#Go back to our original directory
os.chdir(projDir)

if os.environ['BOOST_ROOT'] is None:
    print('Environment variable BOOST_ROOT is not declared. aborting...')
    sys.exit(0)

try:
    setup(name='Linkbot',
        platforms='blah',
        version='2.0.0',
        description='Barobo Linkbot module',
        author='David Ko',
        author_email='david@barobo.com',
        url='http://www.barobo.com',
        packages=['linkbot.demo', 'linkbot'],
        ext_package='linkbot',
        data_files = data_files,
        package_dir={'':'src'},
        #py_modules=['linkbot._linkbot'],
        zip_safe = False,
        ext_modules=[Extension('__stub', sources=['src/stub.cpp'])]
        )
except Exception as e:
    print(e)

