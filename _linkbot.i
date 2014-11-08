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

/* GETTERS */
int linkbotGetAccelerometer(Linkbot *l, int *OUTPUT, double *OUTPUT, 
                            double *OUTPUT, double *OUTPUT);
%{
int linkbotGetFormFactor(Linkbot *l, int *form)
{
    barobo::FormFactor::Type _form;
    int rc;
    if((rc = linkbotGetFormFactor(l, &_form))) {
        return rc;
    }
    *form = _form;
    return 0;
}
%}
int linkbotGetFormFactor(Linkbot *l, int *OUTPUT);
int linkbotGetJointAngles(Linkbot *l, int *OUTPUT, double *OUTPUT, 
                          double *OUTPUT, double *OUTPUT);

%{
int linkbotGetJointStates(Linkbot* l, int *timestamp, int *j1, int* j2, int* j3)
{
    barobo::JointState::Type values[3];
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
int linkbotGetJointSpeeds(Linkbot*, double*OUTPUT, double*OUTPUT, double*OUTPUT);
int linkbotGetLedColor(Linkbot *l, int *OUTPUT, int *OUTPUT, int *OUTPUT);

/* SETTERS */
int linkbotSetBuzzerFrequencyOn(Linkbot *l, float freq);
int linkbotSetEncoderEventThreshold(Linkbot *l, int jointNo, double thresh);
int linkbotSetJointSpeeds(Linkbot *l, int mask, double j1, double j2, 
                          double j3);

/* MOVEMENT */
/*
int linkbotMoveContinuous(Linkbot* l, int mask, 
                          barobo::JointState::Type d1, 
                          barobo::JointState::Type d2, 
                          barobo::JointState::Type d3);
*/
%{
int linkbotMoveContinuous(Linkbot* l, int mask, 
                          int d1, 
                          int d2, 
                          int d3)
{
    return linkbotMoveContinuous(l, mask,
        static_cast<barobo::JointState::Type>(d1),
        static_cast<barobo::JointState::Type>(d2),
        static_cast<barobo::JointState::Type>(d3) );
}
%}
int linkbotMoveContinuous(Linkbot* l, int mask, 
                          int d1, 
                          int d2, 
                          int d3);
int linkbotMove(Linkbot*, int mask, double j1, double j2, double j3);
int linkbotMoveTo(Linkbot*, int mask, double j1, double j2, double j3);
int linkbotDrive(Linkbot*, int mask, double j1, double j2, double j3);
int linkbotDriveTo(Linkbot*, int mask, double j1, double j2, double j3);
int linkbotStop(Linkbot*, int mask);

/* CALLBACKS */
%{
void PythonAccelerometerEventCallback(double x, double y, double z,
                                      int timestamp, void* clientdata)
{
    PyObject *func, *arglist;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    func = (PyObject *) clientdata;               // Get Python function
    arglist = Py_BuildValue("(dddI)",x, y, z, timestamp);             // Build argument list
    PyEval_CallObject(func,arglist);     // Call Python
    Py_DECREF(arglist);                           // Trash arglist
    // Release the thread. No Python API allowed beyond this point.
    PyGILState_Release(gstate);
}

int linkbotSetPythonAccelerometerEventCallback(Linkbot* l, PyObject *pyfunc)
{
    int rc = linkbotSetAccelerometerEventCallback(l, PythonAccelerometerEventCallback, (void*)pyfunc);
    Py_INCREF(pyfunc);
    return rc;
}

int linkbotUnsetPythonAccelerometerEventCallback(Linkbot* l)
{
    return linkbotSetAccelerometerEventCallback(l, NULL, NULL);
}
%}

int linkbotSetPythonAccelerometerEventCallback(Linkbot*, PyObject *pyfunc);
int linkbotUnsetPythonAccelerometerEventCallback(Linkbot* l);

%{
void PythonButtonEventCallback(int buttonNo, 
                               barobo::ButtonState::Type state, 
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

int linkbotSetPythonButtonEventCallback(Linkbot* l, PyObject *pyfunc)
{
    int rc = linkbotSetButtonEventCallback(l, PythonButtonEventCallback, (void*)pyfunc);
    Py_INCREF(pyfunc);
    return rc;
}
int linkbotUnsetPythonButtonEventCallback(Linkbot* l)
{
    return linkbotSetButtonEventCallback(l, NULL, NULL);
}
%}

int linkbotSetPythonButtonEventCallback(Linkbot*, PyObject *pyfunc);
int linkbotUnsetPythonButtonEventCallback(Linkbot* l);

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
    arglist = Py_BuildValue("(bdI)",jointNo+1, anglePosition, timestamp); // Build argument list
    PyEval_CallObject(func,arglist);     // Call Python
    Py_DECREF(arglist);                           // Trash arglist
    // Release the thread. No Python API allowed beyond this point.
    PyGILState_Release(gstate);
}

int linkbotSetPythonEncoderEventCallback(Linkbot* l, double granularity, PyObject *pyfunc)
{
    int rc = linkbotSetEncoderEventCallback(l, PythonEncoderEventCallback, granularity, (void*)pyfunc);
    Py_INCREF(pyfunc);
    return rc;
}
int linkbotUnsetPythonEncoderEventCallback(Linkbot* l)
{
    return linkbotSetEncoderEventCallback(l, NULL, 0, NULL);
}
%}

int linkbotSetPythonEncoderEventCallback(Linkbot*, double granularity, PyObject *pyfunc);
int linkbotUnsetPythonEncoderEventCallback(Linkbot* l);

%{
void PythonJointEventCallback(int jointNo,
                              barobo::JointState::Type state,
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

int linkbotSetPythonJointEventCallback(Linkbot* l, PyObject *pyfunc)
{
    int rc = linkbotSetJointEventCallback(l, PythonJointEventCallback, (void*)pyfunc);
    Py_INCREF(pyfunc);
    return rc;
}
int linkbotUnsetPythonJointEventCallback(Linkbot* l)
{
    return linkbotSetJointEventCallback(l, NULL, NULL);
}
%}

int linkbotSetPythonJointEventCallback(Linkbot* l, PyObject *pyfunc);
int linkbotUnsetPythonJointEventCallback(Linkbot* l);

