#pragma once

#include "Packet.h"

class CircularBuffer;

class PacketDecoder
{
public:
	bool decode(CircularBuffer& buf, Packet& pk);

private:
	static std::size_t findPacket(const CircularBuffer& buf);
};
