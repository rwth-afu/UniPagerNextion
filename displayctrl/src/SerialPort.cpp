#include "SerialPort.h"
#include <cassert>
#include <cstring>
#include <stdexcept>
#include <utility>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>

using namespace std;

SerialPort::SerialPort(const string& port) :
	mHandle(-1)
{
	/*
	 * O_RDWR:
	 * Open port for read/write.
	 *
	 * O_NOCTTY:
	 * We don't want to be the controlling terminal for that port.
	 *
	 * O_NDELAY:
	 * Set to non-blocking mode.
	 */
	mHandle = open(port.c_str(), O_RDWR | O_NOCTTY);
	if (mHandle < 0)
	{
		throw runtime_error(strerror(errno));
	}

	// Setup port to raw mode
	termios tio;
	memset(&tio, 0, sizeof(termios));

	cfmakeraw(&tio);

	// Setup timeouts
	// VMIN: Minimum number of bytes received
	// VTIME: Timeout in 0.1 seconds
	tio.c_cc[VMIN] = 0;
	tio.c_cc[VTIME] = 5;

	// Set baud rate
	cfsetspeed(&tio, B115200);

	tcflush(mHandle, TCIFLUSH);
	tcsetattr(mHandle, TCSANOW, &tio);
}

SerialPort::~SerialPort()
{
	if (mHandle > -1)
	{
		close(mHandle);
	}
}

int SerialPort::write(const void* data, size_t length) const
{
	assert(mHandle > -1);

	auto w = ::write(mHandle, data, length);
	if (w < 0)
	{
		if (errno == EAGAIN || errno == EWOULDBLOCK)
		{
			return 0;
		}
		else
		{
			throw runtime_error(strerror(errno));
		}
	}

	return w;
}

int SerialPort::read(void* data, size_t max) const
{
	assert(mHandle > -1);

	const auto r = ::read(mHandle, data, max);
	if (r < 0)
	{
		if (errno == EAGAIN || errno == EWOULDBLOCK)
		{
			return 0;
		}
		else
		{
			throw runtime_error(strerror(errno));
		}
	}

	return r;
}
