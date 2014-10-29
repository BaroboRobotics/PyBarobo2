%module linkbot
%{
    //#include "PyLinkbotWrapper/src/linkbot_wrapper.hpp"
    #include "../deps/baromesh/include/baromesh/linkbot.h"
%}

namespace barobo {
enum ButtonState {
    UP,
    DOWN
};

enum MotorDir {
    FORWARD,
    BACKWARD,
    NEUTRAL,
    HOLD
};

enum JointState {
    JOINT_STOP,
    JOINT_HOLD,
    JOINT_MOVING,
    JOINT_FAIL
};
}

// Grab a Python function object as a Python object.
%typemap(python,in) PyObject *pyfunc {
    if (!PyCallable_Check($source)) {
        PyErr_SetString(PyExc_TypeError, "Need a callable object!");
        return NULL;
    }
    $target = $source;
}

linkbot_t* Linkbot_new(const char* serialId);

int Linkbot_connect(linkbot_t*);
int Linkbot_disconnect(linkbot_t*);

int Linkbot_move(linkbot_t*, int mask, double j1, double j2, double j3);

%{
void PythonButtonEventCallback(int buttonNo, 
                               barobo::ButtonState state, 
                               int timestamp, 
                               void* clientdata)
{
    PyObject *func, *arglist;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    func = (PyObject *) clientdata;               // Get Python function
    arglist = Py_BuildValue("(bbI)",buttonNo, state, timestamp);             // Build argument list
    PyEval_CallObject(func,arglist);     // Call Python
    Py_DECREF(arglist);                           // Trash arglist
    // Release the thread. No Python API allowed beyond this point.
    PyGILState_Release(gstate);
}

void Linkbot_setPythonButtonEventCallback(linkbot_t* l, PyObject *pyfunc)
{
    Linkbot_setButtonEventCallback(l, PythonButtonEventCallback, (void*)pyfunc);
}
%}

void Linkbot_setPythonButtonEventCallback(linkbot_t*, PyObject *pyfunc);
