
#include "rpc/asio/tcpclient.hpp"
#include "baromesh/iocore.hpp"
#include "baromesh/daemon.hpp"

#include <boost/asio/use_future.hpp>

#include <boost/scope_exit.hpp>


#include <iostream>
#include <cmath>
#include <thread>
#include <mutex>
#include <chrono>
#include <queue>
#include <condition_variable>
#include "baromesh/linkbot.hpp"
#include <boost/python.hpp>
#include <boost/filesystem.hpp>


using namespace boost::python;
using boost::asio::use_future;

struct move_exception : std::exception
{
    move_exception(int motor) : mMotor(motor) { }
    char const* what() const throw() { 
        cnvt << "Motor " << mMotor << " error encountered.";
        return cnvt.str().c_str();
    }

    private:
    static std::ostringstream cnvt;
    int mMotor;
};
std::ostringstream move_exception::cnvt;

void translate_exception(move_exception const& e)
{
    // Use the Python 'C' API to set up an exception object
    PyErr_SetString(PyExc_Warning, e.what());
}

/* The following is used to store and use function argument lists in a delayed
 * manner, as detailed here:
 http://stackoverflow.com/questions/7858817/unpacking-a-tuple-to-call-a-matching-function-pointer
 */
template<int ...>
struct seq { };

template<int N, int ...S>
struct gens : gens<N-1, N-1, S...> { };

template<int ...S>
struct gens<0, S...> {
  typedef seq<S...> type;
};

class Linkbot : public barobo::Linkbot
{
    public:
    Linkbot(const std::string& serialId) 
        : barobo::Linkbot(serialId),
          m_jointStatesDirty(false)
    {
        if (! PyEval_ThreadsInitialized()) {
            PyEval_InitThreads();
        }

        barobo::FormFactor::Type formFactor;
        barobo::Linkbot::getFormFactor(formFactor);
        switch(formFactor) {
            case barobo::FormFactor::I:
                m_motorMask = 0x05;
                break;
            case barobo::FormFactor::L:
                m_motorMask = 0x03;
                break;
            case barobo::FormFactor::T:
                m_motorMask = 0x07;
                break;
        }
    }

    ~Linkbot()
    {
        barobo::Linkbot::setAccelerometerEventCallback(nullptr, nullptr);
        barobo::Linkbot::setButtonEventCallback(nullptr, nullptr);
        barobo::Linkbot::setEncoderEventCallback(nullptr, 0, nullptr);
        barobo::Linkbot::setJointEventCallback(nullptr, nullptr);
        m_accelerometerEventHandler.stop();
        m_buttonEventHandler.stop();
        m_encoderEventHandler.stop();
        m_jointEventHandler.stop();
    }

    void releaseCallbacks()
    {
        /*
        m_buttonEventCbObject = boost::python::object();
        m_encoderEventCbObject = boost::python::object();
        m_jointEventCbObject = boost::python::object();
        m_accelerometerEventCbObject = boost::python::object();
        */
    }

/* GETTERS */

    boost::python::tuple getAccelerometer() {
        int timestamp; 
        double x, y, z;
        barobo::Linkbot::getAccelerometer(timestamp, x, y, z);
        return boost::python::make_tuple(timestamp, x, y, z);
    }

    double getBatteryVoltage() {
        double v;
        barobo::Linkbot::getBatteryVoltage(v);
        return v;
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

    boost::python::tuple getJointSafetyThresholds()
    {
        int t1, t2, t3;
        barobo::Linkbot::getJointSafetyThresholds(t1, t2, t3);
        return boost::python::make_tuple(t1, t2, t3);
    }

    boost::python::tuple getJointSafetyAngles()
    {
        double t1, t2, t3;
        barobo::Linkbot::getJointSafetyAngles(t1, t2, t3);
        return boost::python::make_tuple(t1, t2, t3);
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
        bool waitrc = false;
        int errorcode = 0;
        int jointnum = 1;
        Py_BEGIN_ALLOW_THREADS
        while(!waitrc) {
            waitrc = m_jointStatesCv.wait_for(lock, 
                    std::chrono::milliseconds(2000),
                    [this, mask, &errorcode, &jointnum] {
                        int timestamp;
                        if(!m_jointStatesDirty) {
                            /* We timed out. Get the current joint states */
                            barobo::Linkbot::getJointStates(timestamp, 
                                m_jointStates[0],
                                m_jointStates[1],
                                m_jointStates[2]);
                        }
                        bool moving = false;
                        int jointmask = 1;
                        jointnum = 1;
                        for(auto& s : m_jointStates) {
                            if(mask&jointmask&m_motorMask) {
                                switch(s) {
                                    case barobo::JointState::MOVING:
                                        moving = true;
                                        break;
                                    case barobo::JointState::FAILURE:
                                        errorcode = jointnum;
                                        return true; // Pop out of the thread
                                }
                                if(s == barobo::JointState::MOVING) {
                                    moving = true;
                                }
                            }
                            jointnum++;
                            jointmask <<= 1;
                        }
                        m_jointStatesDirty = false;
                        return !moving;
                    }
            );
        }
        Py_END_ALLOW_THREADS
        if(errorcode) {
            throw move_exception(jointnum);
        }
    }

    void moveAccel(int mask,
        double omega0_i, double timeout0, int modeOnTimeout0,
        double omega1_i, double timeout1, int modeOnTimeout1,
        double omega2_i, double timeout2, int modeOnTimeout2)
    {
        barobo::Linkbot::moveAccel(
            mask, 0,
            omega0_i, timeout0, barobo::JointState::Type(modeOnTimeout0),
            omega1_i, timeout1, barobo::JointState::Type(modeOnTimeout1),
            omega2_i, timeout2, barobo::JointState::Type(modeOnTimeout2));
    }

/* CALLBACKS */

    void setButtonEventCallback(boost::python::object func)
    {
        m_buttonEventHandler.cbObject = func;
        if(func.is_none()) {
            barobo::Linkbot::setButtonEventCallback(
                    nullptr, nullptr);
        } else {
            barobo::Linkbot::setButtonEventCallback(
                    &Linkbot::buttonEventCallback,
                    this);
        }
    }

    static void buttonEventCallback(barobo::Button::Type buttonNo,
                                    barobo::ButtonState::Type event,
                                    int timestamp,
                                    void* userData)
    {
        auto l = static_cast<Linkbot*>(userData);
        l->m_buttonEventHandler.push(buttonNo, event, timestamp);
    }

    void setEncoderEventCallback(boost::python::object func, float granularity)
    {
        m_encoderEventHandler.cbObject = func;
        if(func.is_none()) {
            barobo::Linkbot::setEncoderEventCallback(
                    nullptr, granularity, nullptr);
        } else {
            barobo::Linkbot::setEncoderEventCallback(
                    &Linkbot::encoderEventCallback,
                    granularity,
                    this);
        }
    }

    static void encoderEventCallback(int jointNo,
                                     double anglePosition,
                                     int timestamp,
                                     void* userData)
    {
        auto l = static_cast<Linkbot*>(userData);
        l->m_encoderEventHandler.push(jointNo+1, anglePosition, timestamp);
    }

    void setJointEventCallback(boost::python::object func)
    {
        m_jointEventHandler.cbObject = func;
        if(func.is_none()) {
            barobo::Linkbot::setJointEventCallback(
                    nullptr, nullptr);
        } else {
            barobo::Linkbot::setJointEventCallback(
                    &Linkbot::jointEventCallback,
                    this);
        }
    }

    static void jointEventCallback(int jointNo, 
                                   barobo::JointState::Type event,
                                   int timestamp,
                                   void* userData)
    {
        auto l = static_cast<Linkbot*>(userData);

        l->m_jointEventHandler.push(jointNo, event, timestamp);
    }

    void setAccelerometerEventCallback(boost::python::object func)
    {
        m_accelerometerEventHandler.cbObject = func;
        if(func.is_none()) {
            barobo::Linkbot::setAccelerometerEventCallback(
                    nullptr, nullptr);
        } else {
            barobo::Linkbot::setAccelerometerEventCallback(
                    &Linkbot::accelerometerEventCallback,
                    this);
        }
    }

    static void accelerometerEventCallback(double x,
                                           double y,
                                           double z,
                                           int timestamp,
                                           void* userData)
    {
        auto l = static_cast<Linkbot*>(userData);
        l->m_accelerometerEventHandler.push(x,y,z,timestamp);
    }

    /* MISC */

    void writeEeprom(int addr, boost::python::object buffer) {
        PyObject* py_buffer = buffer.ptr();
        Py_INCREF(py_buffer);
        /* FIXME: The next line should raise an exception in Python */
        if(!PyObject_CheckBuffer(py_buffer)) return;
        Py_buffer view;
        Py_INCREF(&view);
        if(PyObject_GetBuffer(py_buffer, &view, 0)) {
            return;
        }
        barobo::Linkbot::writeEeprom( addr, 
                     static_cast<const uint8_t*>(view.buf), 
                     static_cast<size_t>(view.len));
        PyBuffer_Release(&view);
        Py_DECREF(&view);
        Py_DECREF(py_buffer);
    }

    boost::python::list readEeprom(int addr, int size) {
        uint8_t buf[128];
        barobo::Linkbot::readEeprom(addr, size, buf);
        boost::python::list retval;
        for(int i = 0; i < size; i++) {
            retval.append(buf[i]);
        }
        return retval;
    }

    void writeTwi(int addr, boost::python::object buffer) {
        PyObject* py_buffer = buffer.ptr();
        /* FIXME: The next line should raise an exception in Python */
        if(!PyObject_CheckBuffer(py_buffer)) return;
        Py_buffer view;
        if(PyObject_GetBuffer(py_buffer, &view, 0)) {
            return;
        }
        barobo::Linkbot::writeTwi( addr, 
                     static_cast<const uint8_t*>(view.buf), 
                     static_cast<size_t>(view.len));
        PyBuffer_Release(&view);
    }

    boost::python::list readTwi(int addr, int size) {
        uint8_t buf[128];
        barobo::Linkbot::readTwi(addr, size, buf);
        boost::python::list retval;
        for(int i = 0; i < size; i++) {
            retval.append(buf[i]);
        }
        return retval;
    }

    boost::python::list writeReadTwi(int addr, boost::python::object sendbuf,
        int recvsize) {
        PyObject* py_buffer = sendbuf.ptr();
        /* FIXME: The next line should raise an exception in Python */
        if(!PyObject_CheckBuffer(py_buffer)) return {};
        Py_buffer view;
        if(PyObject_GetBuffer(py_buffer, &view, 0)) {
            return {};
        }
        uint8_t buf[128];
        barobo::Linkbot::writeReadTwi( addr, 
                     static_cast<const uint8_t*>(view.buf), 
                     static_cast<size_t>(view.len),
                     buf,
                     recvsize);
        PyBuffer_Release(&view);
        boost::python::list retval;
        for(int i = 0; i < recvsize; i++) {
            retval.append(buf[i]);
        }
        return retval;
    }

    template <typename... Args> struct EventHandler {
        EventHandler() : active(true) 
        { 
            /* Start the worker thread */
            std::thread cbThread {
                [this] {
                    std::unique_lock<std::mutex> l(lock);
                    while(active) {
                        while( (queue.size() == 0) && (active) ) {
                            cond.wait(l);
                        }
                        l.unlock();
                        delayed_dispatch();
                        l.lock();
                    }
                }};
            thread.swap(cbThread);
        }
        boost::python::object cbObject;
        std::thread thread;
        std::mutex lock;
        std::condition_variable cond;
        bool active;
        std::queue<std::tuple<Args...>> queue;

        void push(Args... args) {
            std::unique_lock<std::mutex> l(lock);
            queue.push(std::make_tuple(args...));
            cond.notify_all();
        }

        void stop() {
            active = false;
            cond.notify_all();
            thread.join();
        }

        void delayed_dispatch() {
            callFunc(typename gens<sizeof...(Args)>::type());
        }

        template<int ...S>
        void callFunc(seq<S...>) {
            if(!cbObject.is_none()) {
                auto params = queue.front();
                queue.pop();
                PyGILState_STATE gstate;
                gstate = PyGILState_Ensure();
                cbObject(std::get<S>(params) ...);
                PyGILState_Release(gstate);
            }
        }
    };

    private:
        int m_motorMask;

        EventHandler<int, int, int> m_buttonEventHandler;
        EventHandler<int, double, int> m_encoderEventHandler;
        EventHandler<double, double, double, int> m_accelerometerEventHandler;
        EventHandler<int, int, int> m_jointEventHandler;

        barobo::JointState::Type m_jointStates[3];
        bool m_jointStatesDirty;
        std::mutex m_jointStatesLock;
        std::condition_variable m_jointStatesCv;

        boost::python::object m_linkbot;
};

void cycleDongle(int seconds) {
    auto ioCore = baromesh::IoCore::get();
    rpc::asio::TcpClient daemon { ioCore->ios(), boost::log::sources::logger() };
    boost::asio::ip::tcp::resolver resolver { ioCore->ios() };
    auto daemonQuery = decltype(resolver)::query {
        baromesh::daemonHostName(), baromesh::daemonServiceName()
    };
    auto daemonIter = resolver.resolve(daemonQuery);
    rpc::asio::asyncInitTcpClient(daemon, daemonIter, use_future).get();
    rpc::asio::asyncConnect<barobo::Daemon>(daemon, std::chrono::seconds(1), use_future).get();
    rpc::asio::asyncFire(daemon,
            rpc::MethodIn<barobo::Daemon>::cycleDongle{2},
            std::chrono::seconds(1), use_future).get();
}

BOOST_PYTHON_MODULE(_linkbot)
{
    register_exception_translator<move_exception>(&translate_exception);
    boost::filesystem::path::imbue(std::locale("C"));
    enum_<barobo::JointState::Type>("JointState")
        .value("coast", barobo::JointState::COAST)
        .value("hold", barobo::JointState::HOLD)
        .value("moving", barobo::JointState::MOVING)
        .value("failure", barobo::JointState::FAILURE);
    #define LINKBOT_FUNCTION(func, docstring) \
    .def(#func, &Linkbot::func, docstring)
    class_<Linkbot,boost::noncopyable>("Linkbot", init<const char*>())
        #include"linkbot_functions.x.h"
        .def("moveWait", &Linkbot::moveWait)
        .def("_releaseCallbacks", &Linkbot::releaseCallbacks)
        .def("setJointStates", static_cast<void (Linkbot::*)(int, 
            barobo::JointState::Type, double,
            barobo::JointState::Type, double,
            barobo::JointState::Type, double)>(&Linkbot::setJointStates))
        ;
    #undef LINKBOT_FUNCTION
    def("cycleDongle", cycleDongle);
}
