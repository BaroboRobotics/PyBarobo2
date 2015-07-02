cmake_minimum_required(VERSION 2.8.12) 
project(pylinkbot CXX)

# Give subprojects access to LinkbotLabs.cmake
#list(INSERT CMAKE_MODULE_PATH 0 "${PROJECT_SOURCE_DIR}/LinkbotLabs/cmake-modules")

#include(LinkbotLabs)
add_subdirectory(LinkbotLabs-SDK)
#ll_add_dependency(baromesh/library baromesh)

##############################################################################
# Boost

# Linking statically to Boost is easier for prototyping. For multi-module
# projects we'll want to use shared libraries and defined -DBOOST_ALL_DYN_LINK
# or the like.
set(Boost_USE_STATIC_LIBS ON)
find_package(Boost 1.54.0 REQUIRED COMPONENTS system log filesystem thread python3)
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
    #$<TARGET_PROPERTY:baromesh,INCLUDE_DIRECTORIES>
    ${PYTHON_INCLUDE_DIRS})

if(WIN32)
    set(suffix ".pyd")
else()
    set(suffix ".so")
endif()

set_target_properties(_linkbot
                      PROPERTIES SUFFIX ${suffix}
                                 PREFIX "")

if(MSVC)
target_link_libraries(_linkbot sfp cxx-util robot-interface
    dongle-interface baromesh rpc ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
else()
target_link_libraries(_linkbot sfp cxx-util robot-interface
    dongle-interface baromesh rpc ${Boost_LIBRARIES} ${PYTHON_LIBRARIES} rt)
endif()
