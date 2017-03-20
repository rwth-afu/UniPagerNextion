#pragma once

#include <atomic>
#include <memory>
#include <thread>

class IBackgroundTask;

class BackgroundWorker
{
public:
	enum class Status
	{
		NEW,
		RUNNING,
		FINISHED,
		FAILED
	};

public:
	explicit BackgroundWorker(std::unique_ptr<IBackgroundTask> task);
	BackgroundWorker(const BackgroundWorker& o) = delete;

	~BackgroundWorker();

	BackgroundWorker& operator=(const BackgroundWorker& o) = delete;

	void start();
	void stop();
	void wait();

	Status getStatus() const;

private:
	void threadProc();

private:
	std::atomic<Status> mStatus;
	std::unique_ptr<IBackgroundTask> mTask;
	std::thread mThread;
};
