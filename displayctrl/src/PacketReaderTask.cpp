#include "PacketReaderTask.h"
#include "SerialPort.h"
#include "CircularBuffer.h"
#include "PacketDecoder.h"
#include <stdexcept>

using namespace std;

PacketReaderTask::PacketReaderTask(shared_ptr<SerialPort> port,
	PacketHandler handler) :
	mQuit(false),
	mPort(move(port)),
	mHandler(move(handler))
{
	if (!mPort)
	{
		throw invalid_argument("Port is null.");
	}

	if (!mHandler)
	{
		throw invalid_argument("Invalid packet handler.");
	}
}

void PacketReaderTask::run()
{
	unsigned char rbuf[64];
	CircularBuffer pkbuf(2048);
	PacketDecoder decoder;
	Packet pk;

	while (!mQuit)
	{
		const auto r = mPort->read(rbuf, sizeof(rbuf));
		if (r < 1)
		{
			continue;
		}

		if (pkbuf.write(rbuf, r) < static_cast<size_t>(r))
		{
			throw runtime_error("Buffer ran out of memory.");
		}

		while (decoder.decode(pkbuf, pk))
		{
			mHandler(pk);
		}
	}
}

void PacketReaderTask::terminate()
{
	mQuit = true;
}
