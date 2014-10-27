#ifndef LINKBOT_WRAPPER_HPP_
#define LINKBOT_WRAPPER_HPP_

#include "baromesh/linkbot.hpp"

void _buttonEventCB(int buttonNo, barobo::ButtonState event, int timestamp, void *data);
void _encoderEventCB(int jointNo, double anglePosition, int timestamp, void *data);
void _accelerometerEventCB(double x, double y, double z, int timestamp, void *data);
void _jointEventCB(int joint, barobo::JointState state, void *data);

class _Linkbot : public barobo::Linkbot {
public:
    _Linkbot();
    _Linkbot(const std::string& serialId);
    virtual ~_Linkbot();

    void formFactor(int & formFactor);

    void enableButtonEvent(bool enable=true);
    void enableEncoderEvent(bool enable=true);
    void enableAccelerometerEvent(bool enable=true);
    void enableJointEvent(bool enable=true);

    void getJointStates(int &timestamp, int &j1, int &j2, int &j3);

    void callTestCB();

    /* Override these */
    virtual void buttonEventCB(int buttonNo, barobo::ButtonState state, int timestamp);
    virtual void encoderEventCB(int joint, double angle, int timestamp);
    virtual void accelerometerEventCB(double x, double y, double z, int timestamp);
    virtual void jointEventCB(int joint, barobo::JointState state, int timestamp);
    virtual void testCB();
};

#endif
