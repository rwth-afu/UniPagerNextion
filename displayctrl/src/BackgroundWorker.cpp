#include "BackgroundWorker.h"
#include "IBackgroundTask.h"
#include <iostream>
#include <stdexcept>

using namespace std;

BackgroundWorker::BackgroundWorker(unique_ptr<IBackgroundTask> task) :
	mStatus(Status::NEW),
	mTask(move(task))
{
	if (!mTask)
	{
		throw invalid_argument("Invalid task");
	}
}

BackgroundWorker::~BackgroundWorker()
{
	try
	{
		stop();
	}
	catch (const exception& ex)
	{
		cerr << "Stopping worker failed: " << ex.what() << endl;
	}
}

void BackgroundWorker::start()
{
	if (!mThread.joinable())
	{
		mThread = thread(&BackgroundWorker::threadProc, this);
		mStatus = Status::RUNNING;
	}
}

void BackgroundWorker::stop()
{
	if (mThread.joinable())
	{
		mTask->terminate();
		mThread.join();
	}
}

void BackgroundWorker::wait()
{
	if (mThread.joinable())
	{
		mThread.join();
	}
}

BackgroundWorker::Status BackgroundWorker::getStatus() const
{
	return mStatus;
}

void BackgroundWorker::threadProc()
{
	try
	{
		mTask->run();
		mStatus = Status::FINISHED;
	}
	catch (const exception& ex)
	{
		cerr << "Task failed: " << ex.what() << endl;
		mStatus = Status::FAILED;
	}
}
