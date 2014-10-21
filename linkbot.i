%module _linkbot
%{
    #include "baromesh/linkbot.hpp"
%}

/* Set up some exception handling */
%include exception.i

%exception {
    try {
        $function
    } catch(...) {
        SWIG_exception(SWIG_RuntimeError, "An exception occured!");
    }
}

namespace barobo{
enum MotorDir {
    FORWARD,
    BACKWARD,
    NEUTRAL,
    HOLD
};

class Linkbot {
public:
    explicit Linkbot (const std::string&);
    std::string serialId () const;

    bool operator== (const Linkbot& that) const {
      return this->serialId() == that.serialId();
    }

    bool operator!= (const Linkbot& that) const {
        return !operator==(that);
    }

    // All member functions may throw a barobo::Error exception on failure.

    void connect ();
    void disconnect ();

    // Member functions take angles in degrees.
    // All functions are non-blocking. Use moveWait() to wait for non-blocking
    // movement functions.
    void drive (int mask, double, double, double);
    void driveTo (int mask, double, double, double);
    void getJointAngles (int& timestamp, double&, double&, double&, int=10);
    void getAccelerometer (int& timestamp, double&, double&, double&);
    void move (int mask, double, double, double);
    void moveContinuous (int mask, MotorDir dir1, MotorDir dir2, MotorDir dir3);
    void moveTo (int mask, double, double, double);
    void moveWait (int mask);
    void setLedColor (int, int, int);
    void setJointEventThreshold (int, double);
    void setJointSpeeds (int mask, double, double, double);
    void stop ();
    void setBuzzerFrequencyOn (float);
    void getVersions (uint32_t&, uint32_t&, uint32_t&);

    typedef void (*ButtonEventCallback)(int buttonNo, ButtonState event, void* userData);
    // JointEventCallback's anglePosition parameter is reported in degrees.
    typedef void (*JointEventCallback)(int jointNo, double anglePosition, void* userData);
    typedef void (*AccelerometerEventCallback)(double x, double y, double z, void* userData);

    // Passing a null pointer as the first parameter of those three functions
    // will disable its respective events.
    void setButtonEventCallback (ButtonEventCallback, void* userData);
    void setJointEventCallback (JointEventCallback, void* userData);
    void setAccelerometerEventCallback (AccelerometerEventCallback, void* userData);
};
}
