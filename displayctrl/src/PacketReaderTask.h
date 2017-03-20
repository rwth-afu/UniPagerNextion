#pragma once

#include "IBackgroundTask.h"
#include "Packet.h"
#include <atomic>
#include <functional>
#include <memory>

class SerialPort;

class PacketReaderTask : public IBackgroundTask
{
public:
	using PacketHandler = std::function<void(const Packet&)>;

public:
	PacketReaderTask(std::shared_ptr<SerialPort> port, PacketHandler handler);

	virtual ~PacketReaderTask() = default;

	virtual void run() override;

	virtual void terminate() override;

private:
	std::atomic_bool mQuit;
	std::shared_ptr<SerialPort> mPort;
	PacketHandler mHandler;
};
