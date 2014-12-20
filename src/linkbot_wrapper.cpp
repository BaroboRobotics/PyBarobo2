#include <cmath>
#include <thread>
#include <mutex>
#include <condition_variable>
#include "baromesh/linkbot.hpp"
#include <boost/python.hpp>

using namespace boost::python;

class Linkbot : public barobo::Linkbot
{
    public:
    Linkbot(const std::string& serialId) 
        : barobo::Linkbot(serialId) 
    {
        if (! PyEval_ThreadsInitialized()) {
            PyEval_InitThreads();
        }
    }

    void connect()
    {
        barobo::Linkbot::connect();

        /* Set up the joint event callback for moveWait() */
        barobo::Linkbot::setJointEventCallback(
                &Linkbot::jointEventCallback,
                this);
    }

/* GETTERS */

    boost::python::tuple getAccelerometer() {
        int timestamp; 
        double x, y, z;
        barobo::Linkbot::getAccelerometer(timestamp, x, y, z);
        return boost::python::make_tuple(timestamp, x, y, z);
    }

    int getFormFactor() {
        barobo::FormFactor::Type form;
        barobo::Linkbot::getFormFactor(form);
        return form;
    }

    boost::python::tuple getJointAngles() {
        int timestamp;
        double j1, j2, j3;
        barobo::Linkbot::getJointAngles(timestamp, j1, j2, j3);
        return boost::python::make_tuple(timestamp, j1, j2, j3);
    }

    boost::python::tuple getJointSpeeds() {
        double j1, j2, j3;
        barobo::Linkbot::getJointSpeeds(j1, j2, j3);
        return boost::python::make_tuple(j1, j2, j3);
    }
    
    boost::python::tuple getJointStates() {
        int timestamp = 0;
        barobo::JointState::Type j1, j2, j3;
        barobo::Linkbot::getJointStates(timestamp, j1, j2, j3);
        boost::python::tuple rc;
        rc += boost::python::make_tuple(timestamp);
        for (auto i : {j1,j2,j3}) {
            rc += boost::python::make_tuple(static_cast<int>(i));
        }
        return rc;
    }
    
    boost::python::tuple getLedColor() {
        int r, g, b;
        barobo::Linkbot::getLedColor(r, g, b);
        return boost::python::make_tuple(r, g, b);
    }

    boost::python::tuple getVersions()
    {
        uint32_t v1, v2, v3;
        barobo::Linkbot::getVersions(v1, v2, v3);
        return boost::python::make_tuple(v1, v2, v3);
    }

/* MOVEMENT */

    void moveWait(int mask=0x07)
    {
        std::unique_lock<std::mutex> lock(m_jointStatesLock);
        int timestamp;
        barobo::Linkbot::getJointStates(timestamp, 
                       m_jointStates[0],
                       m_jointStates[1],
                       m_jointStates[2]);
        Py_BEGIN_ALLOW_THREADS
        m_jointStatesCv.wait(lock, 
            [this, mask] {
                bool moving = false;
                int jointmask = 1;
                for(auto& s : m_jointStates) {
                    if(mask&jointmask) {
                        if(s == barobo::JointState::MOVING) {
                            moving = true;
                            break;
                        }
                    }
                    jointmask <<= 1;
                }
                return !moving;
            }
            );
        Py_END_ALLOW_THREADS
    }

/* CALLBACKS */

    void setButtonEventCallback(boost::python::object func)
    {
        m_buttonEventCbObject = func;
        if(func.is_none()) {
            barobo::Linkbot::setButtonEventCallback(
                    nullptr, nullptr);
        } else {
            barobo::Linkbot::setButtonEventCallback(
                    &Linkbot::buttonEventCallback,
                    &m_buttonEventCbObject);
        }
    }

    static void buttonEventCallback(int buttonNo,
                                    barobo::ButtonState::Type event,
                                    int timestamp,
                                    void* userData)
    {
        std::thread cbThread( &Linkbot::buttonEventCallbackThread,
                              buttonNo,
                              event,
                              timestamp,
                              userData);
        cbThread.detach();
    }

    static void buttonEventCallbackThread(int buttonNo,
                                    barobo::ButtonState::Type event,
                                    int timestamp,
                                    void* userData)
    {
        /* Lock the Python GIL */
        PyGILState_STATE gstate;
        gstate = PyGILState_Ensure();

        /* The userData should be a python object */
        boost::python::object* func =
            static_cast<boost::python::object*>(userData);
        if(!func->is_none()) {
            (*func)(buttonNo, static_cast<int>(event), timestamp);
        }

        /* Release the Python GIL */
        PyGILState_Release(gstate);
    }

    void setEncoderEventCallback(boost::python::object func, float granularity)
    {
        m_encoderEventCbObject = func;
        if(func.is_none()) {
            barobo::Linkbot::setEncoderEventCallback(
                    nullptr, granularity, nullptr);
        } else {
            barobo::Linkbot::setEncoderEventCallback(
                    &Linkbot::encoderEventCallback,
                    granularity,
                    &m_encoderEventCbObject);
        }
    }

    static void encoderEventCallback(int jointNo,
                                     double anglePosition,
                                     int timestamp,
                                     void* userData)
    {
        std::thread cbThread ( &Linkbot::encoderEventCallbackThread,
                               jointNo,
                               anglePosition,
                               timestamp,
                               userData );
        cbThread.detach();
    }

    static void encoderEventCallbackThread(int jointNo,
                                    double anglePosition,
                                    int timestamp,
                                    void* userData)
    {
        /* Lock the Python GIL */
        PyGILState_STATE gstate;
        gstate = PyGILState_Ensure();

        /* The userData should be a python object */
        boost::python::object* func =
            static_cast<boost::python::object*>(userData);
        if(!func->is_none()) {
            (*func)(jointNo+1, anglePosition, timestamp);
        }

        /* Release the Python GIL */
        PyGILState_Release(gstate);
    }

    void setJointEventCallback(boost::python::object func)
    {
        m_jointEventCbObject = func;
    }

    static void jointEventCallback(int jointNo, 
                                   barobo::JointState::Type event,
                                   int timestamp,
                                   void* userData)
    {
        auto l = static_cast<Linkbot*>(userData);

        std::unique_lock<std::mutex> lock(l->m_jointStatesLock);
        l->m_jointStates[jointNo] = event;
        l->m_jointStatesCv.notify_all();
        lock.unlock();

        auto &func = l->m_jointEventCbObject;
        if(!func.is_none()) {
            /* Lock the Python GIL */
            PyGILState_STATE gstate;
            gstate = PyGILState_Ensure();

            (func)(jointNo, static_cast<int>(event), timestamp);

            /* Release the Python GIL */
            PyGILState_Release(gstate);
        }

    }

    void setAccelerometerEventCallback(boost::python::object func)
    {
        m_accelerometerEventCbObject = func;
        if(func.is_none()) {
            barobo::Linkbot::setAccelerometerEventCallback(
                    nullptr, nullptr);
        } else {
            barobo::Linkbot::setAccelerometerEventCallback(
                    &Linkbot::accelerometerEventCallback,
                    &m_accelerometerEventCbObject);
        }
    }

    static void accelerometerEventCallback(double x,
                                           double y,
                                           double z,
                                           int timestamp,
                                           void* userData)
    {
        std::thread cbThread( &Linkbot::accelerometerEventCallbackThread,
                              x, y, z, timestamp, userData);
        cbThread.detach();
    }

    static void accelerometerEventCallbackThread(double x,
                                           double y,
                                           double z,
                                           int timestamp,
                                           void* userData)
    {
        /* Lock the Python GIL */
        PyGILState_STATE gstate;
        gstate = PyGILState_Ensure();

        /* The userData should be a python object */
        boost::python::object* func =
            static_cast<boost::python::object*>(userData);
        if(!func->is_none()) {
            (*func)(x, y, z, timestamp);
        }

        /* Release the Python GIL */
        PyGILState_Release(gstate);
    }

    private:
        boost::python::object m_buttonEventCbObject;
        boost::python::object m_encoderEventCbObject;
        boost::python::object m_jointEventCbObject;
        boost::python::object m_accelerometerEventCbObject;

        barobo::JointState::Type m_jointStates[3];
        std::mutex m_jointStatesLock;
        std::condition_variable m_jointStatesCv;
};

BOOST_PYTHON_MODULE(_linkbot)
{
    #define LINKBOT_FUNCTION(func, docstring) \
    .def(#func, &Linkbot::func, docstring)
    class_<Linkbot,boost::noncopyable>("Linkbot", init<const char*>())
        #include"linkbot_functions.x.h"
        .def("moveWait", &Linkbot::moveWait)
        ;
    #undef LINKBOT_FUNCTION
}
