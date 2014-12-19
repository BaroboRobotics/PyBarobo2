cmake_minimum_required(VERSION 2.8.12) 
project(pylinkbot CXX)

add_subdirectory(../deps/baromesh baromesh)
##############################################################################
# Boost

# Linking statically to Boost is easier for prototyping. For multi-module
# projects we'll want to use shared libraries and defined -DBOOST_ALL_DYN_LINK
# or the like.
set(Boost_USE_STATIC_LIBS ON)
find_package(Boost 1.54.0 REQUIRED COMPONENTS system log filesystem thread python)
find_package(Threads)
find_package(PythonLibs 3)

set(SOURCES
    src/linkbot_wrapper.cpp
    )

add_library(_linkbot SHARED ${SOURCES})

set_source_files_properties(${SOURCES}
    PROPERTIES COMPILE_FLAGS 
    "-std=c++11 -ftemplate-depth-128 -O0 -fno-inline -fPIC")

add_definitions(-DBOOST_ALL_NO_LIB=1 -DBOOST_PYTHON_SOURCE)

target_include_directories(_linkbot
    PUBLIC
    $<TARGET_PROPERTY:baromesh,INCLUDE_DIRECTORIES>
    ${PYTHON_INCLUDE_DIRS})

if(WIN32)
set_target_properties(_linkbot
                      PROPERTIES SUFFIX ".pyd"
                                 PREFIX "")
else()
set_target_properties(_linkbot
                      PROPERTIES SUFFIX ".so"
                                 PREFIX "")
endif()

target_link_libraries(_linkbot sfp cxx-util robot-interface
    dongle-interface baromesh rpc ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
