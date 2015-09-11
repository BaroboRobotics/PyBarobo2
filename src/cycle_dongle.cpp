
#include "rpc/asio/client.hpp"
#include "baromesh/iocore.hpp"
#include "baromesh/daemon.hpp"

#include <boost/asio/use_future.hpp>

#include <boost/scope_exit.hpp>

using boost::asio::use_future;

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

