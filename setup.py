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
projDir = os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh')
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

boost_libs = ['log', 'thread', 'system', 'filesystem']

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
    subprocess.check_call(['mingw32-make', 'baromesh', 'VERBOSE=1'])
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
          'dlls/libwinpthread-1.dll'])]
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
    boost_libraries = []
    for lib in boost_libs:
        boost_libraries += ['boost_'+lib]
    libraries += boost_libraries
    data_files = None

#Go back to our original directory
os.chdir(origCWD)

if os.environ['BOOST_ROOT'] is None:
    print('Environment variable BOOST_ROOT is not declared. aborting...')
    sys.exit(0)

try:
    setup(name='Linkbot',
        version='2.0.0',
        description='Barobo Linkbot module',
        author='David Ko',
        author_email='david@barobo.com',
        url='http://www.barobo.com',
        packages=['demo'],
        ext_package='linkbot',
        ext_modules=[Extension('__linkbot', 
          sources=['_linkbot.i'],
          swig_opts=['-threads', '-c++', '-v'],
          include_dirs=[
            os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh', 'include'),
            ],
          library_dirs=[
            os.path.join(buildDir),
            os.path.join(buildDir, 'libsfp'),
            os.path.join(buildDir, 'ribbon-bridge'),
            os.path.join(buildDir, 'ribbon-bridge-interfaces'),
            os.path.join(os.environ['BOOST_ROOT'], 'stage', 'lib'),
            buildDir],
          libraries=libraries,
          extra_compile_args=['-g'],
          extra_link_args=['-g'],
          )],
        package_dir={'linkbot':''},
        py_modules=['linkbot._linkbot'],
        zip_safe = False,
        data_files = data_files,
        )
except Exception as e:
    print(e)

