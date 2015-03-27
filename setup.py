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

PyLinkbot_Version = '2.2.0'

projDir = os.getcwd()
# projDir = os.path.dirname(origCWD)
# projDir = os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh')
buildDir = os.path.join(projDir, 'build-ext-'+ platform.platform())
stageDir = os.path.join(projDir, 'stage-'+ platform.platform())

try:
    buildDir += os.path.basename(os.environ['CXX'])
    stageDir += os.path.basename(os.environ['CXX'])
except:
    pass

try:
    if not os.path.isdir(buildDir):
        os.mkdir(buildDir)
except Exception as e:
    print('Could not create build directory:')
    print(buildDir)
    print('Aborting build...')
    sys.exit(0)

try:
    try:
        shutil.rmtree(stageDir)
    except:
        pass
    if not os.path.isdir(stageDir):
        os.mkdir(stageDir)
except Exception as e:
    print('Could not create staging directory:')
    print(stageDir)
    print('Aborting build...')
    sys.exit(0)

# Copy modules to staging directory
shutil.copytree(os.path.join(projDir, 'src', 'linkbot'), 
    os.path.join(stageDir, 'linkbot'))

# Go to the build directory
os.chdir(buildDir)

if platform.system() == 'Windows':
    mingw_version='49'
    # Build our C/C++ library into our tempdir staging directory
    if not os.path.exists(os.path.join(buildDir, 'Makefile')):
        subprocess.check_call([
                'cmake', 
                projDir])
    subprocess.check_call(['cmake', '--build', '.', '--config', 'release', ])
    shutil.copy(os.path.join(buildDir, 'release', '_linkbot.pyd'),
        os.path.join(projDir, 'src','linkbot', '_linkbot.pyd'))
    dlls = ['msvcp120.dll', 'msvcr120.dll']
    for dll in dlls:
        shutil.copy(os.path.join(projDir, 'dlls', dll),
            os.path.join(stageDir, 'linkbot', dll))
    package_data = {'linkbot': ['_linkbot.pyd']+dlls}
else:
    # Build our C/C++ library into our tempdir staging directory
    if not os.path.exists(os.path.join(buildDir, 'Makefile')):
        subprocess.check_call([
                'cmake', 
                '-G', 'Unix Makefiles', 
                '-DCMAKE_CXX_FLAGS=-fPIC', 
                '-DBUILD_SHARED_LIBS=OFF',
                '-DCMAKE_BUILD_TYPE=Release',
                projDir])
    subprocess.check_call(['make', 'VERBOSE=1'])
    shutil.copy(os.path.join(buildDir, '_linkbot.so'),
        os.path.join(stageDir, 'linkbot', '_linkbot.so'))
    package_data = {'linkbot': ['_linkbot.so']}

#Go back to our original directory
os.chdir(projDir)

if os.environ['BOOST_ROOT'] is None:
    print('Environment variable BOOST_ROOT is not declared. aborting...')
    sys.exit(0)

try:
    import codecs
    here = os.path.abspath(os.path.dirname(__file__))
    README = codecs.open(os.path.join(here, 'README.txt'), encoding='utf8').read()
    CHANGES = codecs.open(os.path.join(here, 'CHANGES.txt'), encoding='utf8').read()
    setup(name='PyLinkbot',
        version=PyLinkbot_Version,
        description='Barobo Linkbot package',
        long_description=README + '\n\n' +  CHANGES,
        author='David Ko',
        author_email='david@barobo.com',
        url='http://www.barobo.com',
        packages=['linkbot.demo', 'linkbot'],
        ext_package='linkbot',
        download_url='http://wiki.linkbotlabs.com/wiki/Learning_Python_3_with_the_Linkbot/Downloads',
        #data_files = data_files,
        package_data = package_data,
        package_dir={'':stageDir},
        #py_modules=['linkbot._linkbot'],
        zip_safe = False,
        ext_modules=[Extension('__stub', sources=['src/stub.cpp'])],
        license='GPL'
        )
except Exception as e:
    print(e)

