#pragma once

class IBackgroundTask
{
public:
	virtual ~IBackgroundTask() = default;

	virtual void run() = 0;

	virtual void terminate() = 0;
};
