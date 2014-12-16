#include <cmath>
#include "baromesh/linkbot.hpp"
#include <boost/python.hpp>

using namespace boost::python;

BOOST_PYTHON_MODULE(_linkbot)
{
    class_<barobo::Linkbot,boost::noncopyable>("Linkbot", init<const char*>())
        .def("connect", &barobo::Linkbot::connect)
        .def("move", &barobo::Linkbot::move)
        ;
}
