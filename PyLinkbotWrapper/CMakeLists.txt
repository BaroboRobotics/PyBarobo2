cmake_minimum_required(VERSION 2.8.12) 
project(pylinkbotwrapper CXX)

##############################################################################
# Boost

# FindBoost.cmake uses BOOST_ROOT as a hint for where to look.
if(NOT DEFINED BOOST_ROOT)
    if(DEFINED ENV{BOOST_ROOT})
        set(BOOST_ROOT "$ENV{BOOST_ROOT}")
    else()
        message(WARNING "BOOST_ROOT is undefined.\nIf Boost libraries fail to "
            "be found, try setting -DBOOST_ROOT=/path/to/boost on the CMake "
            "command line.\n")
    endif()
endif()

# Linking statically to Boost is easier for prototyping. For multi-module
# projects we'll want to use shared libraries and defined -DBOOST_ALL_DYN_LINK
# or the like.
set(Boost_USE_STATIC_LIBS ON)
find_package(Boost 1.54.0 REQUIRED COMPONENTS system log filesystem thread)

add_subdirectory(../../ LinkbotLabs)

set(SOURCES
    src/linkbot_wrapper.cpp
    )

add_library(linkbot_wrapper ${SOURCES})

set_source_files_properties(${SOURCES}
    PROPERTIES COMPILE_FLAGS "-std=c++11")

target_include_directories(linkbot_wrapper
    PUBLIC $<TARGET_PROPERTY:sfp,INCLUDE_DIRECTORIES>
           $<TARGET_PROPERTY:robot-interface,INCLUDE_DIRECTORIES>
           $<TARGET_PROPERTY:baromesh,INCLUDE_DIRECTORIES>
           $<TARGET_PROPERTY:cxx-util,INTERFACE_INCLUDE_DIRECTORIES>
           ${Boost_INCLUDE_DIRS}
           include
    )
target_link_libraries(linkbot_wrapper
    PUBLIC sfp cxx-util
           robot-interface dongle-interface
           baromesh
           rpc 
           ${Boost_LIBRARIES}
    )

if(WIN32)
    target_link_libraries(linkbot_wrapper
        PRIVATE setupapi
        )
endif()

