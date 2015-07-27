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
if sys.version_info[0] < 3:
    import urllib as urlrequest
else:
    import urllib.request as urlrequest

PyLinkbot_Version = '2.3.3'
LinkbotLabs_SDK_branch = '56739cf1e08a34ec3f5401abd92135917c3d61ad'

projDir = os.getcwd()
# projDir = os.path.dirname(origCWD)
# projDir = os.path.join(os.path.dirname(origCWD), 'deps', 'baromesh')
buildDir = os.path.join(projDir, 'build-ext-'+ platform.platform())
stageDir = os.path.join(projDir, 'stage-'+ platform.platform())
depsDir = os.path.join(projDir, 'deps-'+platform.platform())

try:
    buildDir += os.path.basename(os.environ['CXX'])
    stageDir += os.path.basename(os.environ['CXX'])
except:
    pass

toolchainFile = None
try:
    toolchainFile = os.environ['CMAKE_TOOLCHAIN_FILE']
    buildDir += '-'+'crosscompile'
    stageDir += '-'+'crosscompile'
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
package_data = {}

def build_boost():
    # Download Boost
    try:
        print('Downloading and building Boost...')
        boostFile = os.path.join(depsDir, 'boost_1_57_0.tar.bz2')
        boostDir = os.path.join(depsDir, 'boost_1_57_0')
        if not os.path.exists(boostFile):
            urlrequest.urlretrieve('http://downloads.sourceforge.net/project/boost/boost/1.57.0/boost_1_57_0.tar.bz2',
                boostFile)
        if not os.path.isdir(boostDir):
            subprocess.check_call(['tar', '-C', depsDir, '-xjf', boostFile])

        os.chdir(boostDir)
        if not os.path.exists(os.path.join(boostDir, 'b2')):
            if sys.version_info[0] < 3:
                subprocess.check_call(['sh', 'bootstrap.sh'])
            else:
                subprocess.check_call(['sh', 'bootstrap.sh',
                    '--with-python=python3.4'])
        boost_modules = [
            'date_time', 
            'filesystem',
            'log',
            'program_options',
            'python',
            'system',
            'thread']
        b2_build_args = ['link=static', 'variant=release', 'cxxflags=-fPIC',
            'cflags=-fPIC']
        for m in boost_modules:
            b2_build_args += ['--with-'+m]
        subprocess.check_call(['./b2'] + b2_build_args)
        os.chdir(buildDir)

        # Set up our environment variables
        os.environ['BOOST_ROOT'] = boostDir
    except:
        print('Could not download boost. Aborting build...')
        sys.exit(0)

def build_nanopb():
    # Download nanopb
    try:
        print('Downloading nanopb...')
        nanopbFile = os.path.join(depsDir, 'nanopb-0.3.1-linux-x86.tar.gz')
        nanopbDir = os.path.join(depsDir, 'nanopb-0.3.1-linux-x86')
        if not os.path.exists(nanopbFile):
            urlrequest.urlretrieve('http://koti.kapsi.fi/~jpa/nanopb/download/nanopb-0.3.1-linux-x86.tar.gz',
                nanopbFile)
        if not os.path.isdir(nanopbDir):
            subprocess.check_call(['tar', '-C', depsDir, '-xzf', nanopbFile])

        # Set up environment variables
        os.environ['NANOPB_ROOT'] = nanopbDir
    except:
        print('Could not download/extract nanopb. Aborting build...')
        sys.exit(0)

    # Checkout the latest Linkbot Labs sdk
    try:
        print('Checking out LinkbotLabs-SDK...')
        sdkDir = os.path.join(projDir, 'LinkbotLabs-SDK')
        if not os.path.isdir(sdkDir):
            subprocess.check_call(['git', 'clone',
                'https://github.com/BaroboRobotics/LinkbotLabs-SDK.git',
                sdkDir])
        os.chdir(sdkDir)
        subprocess.check_call(['git', 'checkout', LinkbotLabs_SDK_branch])
        subprocess.check_call(['git', 'submodule', 'update', 
            '--recursive', '--init'])
        os.chdir(buildDir)
    except:
        print('Could not download/extract LinkbotLabs-SDK. Aborting build...')
        sys.exit(0)


if platform.system() == 'Windows':
    mingw_version='49'
    # Build our C/C++ library into our tempdir staging directory
    if not os.path.exists(os.path.join(buildDir, 'Makefile')):
        subprocess_args = [ 'cmake', projDir]
        if toolchainFile is not None:
            subprocess_args += ['-DCMAKE_TOOLCHAIN_FILE='+toolchainFile]
        subprocess.check_call(subprocess_args)
    subprocess.check_call(['cmake', '--build', '.', '--config', 'release', ])
    shutil.copy(os.path.join(buildDir, 'release', '_linkbot.pyd'),
        os.path.join(projDir, 'src','linkbot', '_linkbot.pyd'))
    dlls = ['msvcp120.dll', 'msvcr120.dll']
    for dll in dlls:
        shutil.copy(os.path.join(projDir, 'dlls', dll),
            os.path.join(stageDir, 'linkbot', dll))
    package_data = {'linkbot': ['_linkbot.pyd']+dlls}
else:
    # Make sure we have all required dependencies
    if 'build' in sys.argv:
        try:
            if not os.path.isdir(depsDir):
                os.mkdir(depsDir)
        except:
            print('Could not create deps directory:')
            print(depsDir)
            print('Aborting build...')
            sys.exit(0)

        if 'BOOST_ROOT' not in os.environ:
            build_boost()

        if 'NANOPB_ROOT' not in os.environ:
            build_nanopb()

        # Build our C/C++ library into our tempdir staging directory
        print('Building Linkbot library...')
        if not os.path.exists(os.path.join(buildDir, 'Makefile')):
            subprocess_args = [
                    'cmake', 
                    '-G', 'Unix Makefiles', 
                    '-DCMAKE_CXX_FLAGS=-fPIC', 
                    '-DBUILD_SHARED_LIBS=OFF',
                    '-DCMAKE_BUILD_TYPE=Release']
            if toolchainFile is not None:
                subprocess_args += ['-DCMAKE_TOOLCHAIN_FILE='+toolchainFile]
            subprocess_args += [projDir]
            subprocess.check_call(subprocess_args)
        subprocess.check_call(['make', 'VERBOSE=1'])
        shutil.copy(os.path.join(buildDir, '_linkbot.so'),
            os.path.join(stageDir, 'linkbot', '_linkbot.so'))

    package_data = {'linkbot': ['_linkbot.so']}

#Go back to our original directory
os.chdir(projDir)

try:
    if 'sdist' in sys.argv:
        package_dir={'':'src'}
    else:
        package_dir={'':stageDir}
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
        package_dir=package_dir,
        #py_modules=['linkbot._linkbot'],
        zip_safe = False,
        ext_modules=[Extension('__stub', sources=['src/stub.cpp'])],
        license='GPL'
        )
except Exception as e:
    print(e)

