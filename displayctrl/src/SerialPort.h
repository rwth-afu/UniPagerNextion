#pragma once

#include <cstddef>
#include <string>

class SerialPort
{
public:
	explicit SerialPort(const std::string& port);
	SerialPort(const SerialPort& o) = delete;

	~SerialPort();

	SerialPort& operator=(const SerialPort& o) = delete;

	int write(const void* data, std::size_t length) const;
	int read(void* data, std::size_t max) const;

private:
	int mHandle;
};
