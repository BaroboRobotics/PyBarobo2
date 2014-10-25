#include <iostream>
#include "linkbot_wrapper.hpp"

void _buttonEventCB(int buttonNo, barobo::ButtonState event, int timestamp, void* data)
{
    _Linkbot *l = static_cast<_Linkbot*>(data);
    l->buttonEventCB(buttonNo, event, timestamp);
    //l->buttonEventCB(buttonNo, 0, timestamp);

}

void _encoderEventCB(int jointNo, double anglePosition, int timestamp, void *data)
{
    _Linkbot *l = static_cast<_Linkbot*>(data);
    l->encoderEventCB(jointNo, anglePosition, timestamp);
}

void _accelerometerEventCB(double x, double y, double z, int timestamp, void* data)
{
    _Linkbot *l = static_cast<_Linkbot*>(data);
    l->accelerometerEventCB(x, y, z, timestamp);
}

void _jointEventCB(int joint, barobo::JointState state, int timestamp, void *data)
{
    _Linkbot *l = static_cast<_Linkbot*>(data);
    l->jointEventCB(joint, state, timestamp);
}

_Linkbot::_Linkbot() : barobo::Linkbot("ABCD") 
{
}

_Linkbot::_Linkbot(const std::string& serialId) : barobo::Linkbot(serialId)
{
    // Make sure the GIL has been created since we need to acquire it in our
    // callback to safely call into the python application.
    /*
    if (! PyEval_ThreadsInitialized()) {
        PyEval_InitThreads();
    }
    */
}

_Linkbot::~_Linkbot()
{}

void _Linkbot::formFactor(int & formFactor)
{
    barobo::FormFactor form;
    getFormFactor(form);
    formFactor = int(form);
}

void _Linkbot::enableButtonEvent(bool enable)
{
    if(enable) {
        setButtonEventCallback(_buttonEventCB, this);
    } else {
        setButtonEventCallback(nullptr, nullptr);
    }
}

void _Linkbot::enableEncoderEvent(bool enable)
{
    if(enable) {
        setEncoderEventCallback(_encoderEventCB, this);
    } else {
        setEncoderEventCallback(nullptr, nullptr);
    }
}

void _Linkbot::enableAccelerometerEvent(bool enable)
{
    if(enable) {
        setAccelerometerEventCallback(_accelerometerEventCB, this);
    } else {
        setAccelerometerEventCallback(nullptr, nullptr);
    }
}

void _Linkbot::enableJointEvent(bool enable)
{
    if(enable) {
        setJointEventCallback(_jointEventCB, this);
    } else {
        setJointEventCallback(nullptr, nullptr);
    }
}

void _Linkbot::callTestCB()
{
    testCB();
}

void _Linkbot::buttonEventCB(int buttonNo, barobo::ButtonState state, int timestamp)
{}

void _Linkbot::encoderEventCB(int joint, double angle, int timestamp)
{}
    
void _Linkbot::accelerometerEventCB(double x, double y, double z, int timestamp)
{}

void _Linkbot::jointEventCB(int joint, barobo::JointState state, int timestamp)
{}

void _Linkbot::testCB()
{
    std::cout << "Hello from C++ land." << std::endl;
}
