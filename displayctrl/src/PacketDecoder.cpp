#include "PacketDecoder.h"
#include "CircularBuffer.h"

using namespace std;

bool PacketDecoder::decode(CircularBuffer& buf, Packet& pk)
{
	const auto size = findPacket(buf);
	if (size > 0)
	{
		// Resize does initialize values to default
		pk.resize(size);

		// TODO Test for size?
		if (buf.read(pk.data(), pk.size()) > 0)
		{
			return true;
		}
	}

	return false;
}

size_t PacketDecoder::findPacket(const CircularBuffer& buf)
{
	if (buf.getSize() < 4)
	{
		// Since each packet ends with 0xFF 0xFF 0xFF we can't have a valid
		// packet with less than 4 bytes of readable data.
		return 0;
	}

	int counter = 0;
	for (size_t i = 0; i < buf.getSize(); ++i)
	{
		if (buf.readByte(i) == 0xFF)
		{
			++counter;

			if (counter == 3)
			{
				// Packet end marker found; adjust index to match packet size
				return (i + 1);
			}
		}
		else
		{
			counter = 0;
		}
	}

	return 0;
}
