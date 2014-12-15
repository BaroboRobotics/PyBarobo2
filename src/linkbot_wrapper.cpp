#include "barobo/linkbot.hpp"
#include <boost/python.hpp>

using namespace boost::python;

BOOST_PYTHON_MODULE(_linkbot)
{
    class_<Linkbot>("Linkbot", init<const char*>())
        .def("connect", &Linkbot::connect)
        .def("move", &Linkbot::move)
        ;
}
