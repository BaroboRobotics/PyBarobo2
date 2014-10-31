%module _linkbot
%{
    //#include "PyLinkbotWrapper/src/linkbot_wrapper.hpp"
    #include "../deps/baromesh/include/baromesh/linkbot.h"
%}

%{
void linkbotPythonInit(void)
{
    // Make sure the GIL has been created since we need to acquire it in our
    // callback to safely call into the python application.
    if (! PyEval_ThreadsInitialized()) {
            PyEval_InitThreads();
    }
}
%}

void linkbotPythonInit(void);

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

typedef struct Linkbot Linkbot;

Linkbot* linkbotNew(const char* serialId);

int linkbotConnect(Linkbot*);
int linkbotDisconnect(Linkbot*);

%{
int linkbotGetFormFactor(Linkbot *l, int *form)
{
    barobo::FormFactor _form;
    int rc;
    if((rc = linkbotGetFormFactor(l, &_form))) {
        return rc;
    }
    *form = _form;
    return 0;
}
%}
int linkbotGetFormFactor(Linkbot *l, int *OUTPUT);

%{
int linkbotGetJointStates(Linkbot* l, int *timestamp, int *j1, int* j2, int* j3)
{
    barobo::JointState values[3];
    int rc;
    if((rc = linkbotGetJointStates(l, timestamp, &values[0], &values[1],
        &values[2])))
    {
        return rc;
    }
    *j1 = values[0];
    *j2 = values[1];
    *j3 = values[2];
    return 0;
}
%}
int linkbotGetJointStates(Linkbot*, int *OUTPUT, int *OUTPUT, int *OUTPUT, int
                          *OUTPUT);

int linkbotMove(Linkbot*, int mask, double j1, double j2, double j3);
int linkbotMoveTo(Linkbot*, int mask, double j1, double j2, double j3);

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

void linkbotSetPythonButtonEventCallback(Linkbot* l, PyObject *pyfunc)
{
    linkbotSetButtonEventCallback(l, PythonButtonEventCallback, (void*)pyfunc);
    Py_INCREF(pyfunc);
}
%}

void linkbotSetPythonButtonEventCallback(Linkbot*, PyObject *pyfunc);

%{
void PythonEncoderEventCallback(int jointNo,
                                double anglePosition,
                                int timestamp,
                                void* clientdata)
{
    PyObject *func, *arglist;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    func = (PyObject *) clientdata;               // Get Python function
    arglist = Py_BuildValue("(bdI)",jointNo, anglePosition, timestamp); // Build argument list
    PyEval_CallObject(func,arglist);     // Call Python
    Py_DECREF(arglist);                           // Trash arglist
    // Release the thread. No Python API allowed beyond this point.
    PyGILState_Release(gstate);
}

void linkbotSetPythonEncoderEventCallback(Linkbot* l, PyObject *pyfunc)
{
    linkbotSetEncoderEventCallback(l, PythonEncoderEventCallback, (void*)pyfunc);
    Py_INCREF(pyfunc);
}
%}

void linkbotSetPythonEncoderEventCallback(Linkbot*, PyObject *pyfunc);

%{
void PythonJointEventCallback(int jointNo,
                              barobo::JointState state,
                              int timestamp,
                              void* clientdata)
{
    PyObject *func, *arglist;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    func = (PyObject *) clientdata;               // Get Python function
    arglist = Py_BuildValue("(bbI)",jointNo, state, timestamp); // Build argument list
    PyEval_CallObject(func,arglist);     // Call Python
    Py_DECREF(arglist);                           // Trash arglist
    // Release the thread. No Python API allowed beyond this point.
    PyGILState_Release(gstate);
}

void linkbotSetPythonJointEventCallback(Linkbot* l, PyObject *pyfunc)
{
    linkbotSetJointEventCallback(l, PythonJointEventCallback, (void*)pyfunc);
    Py_INCREF(pyfunc);
}
%}

void linkbotSetPythonJointEventCallback(Linkbot* l, PyObject *pyfunc);

