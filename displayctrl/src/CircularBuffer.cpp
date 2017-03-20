#include "CircularBuffer.h"
#include <algorithm>
#include <cassert>
#include <cstring>
#include <stdexcept>

using namespace std;

CircularBuffer::CircularBuffer(size_t capacity) :
	mCapacity(capacity),
	mSize(0),
	mReadIdx(0),
	mWriteIdx(0),
	mData(nullptr)
{
	if (mCapacity < 1)
	{
		throw invalid_argument("Invalid capacity.");
	}

	mData = new unsigned char[mCapacity];
}

CircularBuffer::CircularBuffer(const CircularBuffer& o) :
	mCapacity(o.mCapacity),
	mSize(o.mSize),
	mReadIdx(o.mReadIdx),
	mWriteIdx(o.mWriteIdx),
	mData(nullptr)
{
	mData = new unsigned char[mCapacity];
	memcpy(mData, o.mData, mSize);
}

CircularBuffer::CircularBuffer(CircularBuffer&& o) :
	mCapacity(o.mCapacity),
	mSize(o.mSize),
	mReadIdx(o.mReadIdx),
	mWriteIdx(o.mWriteIdx),
	mData(o.mData)
{
	o.mCapacity = 0;
	o.mSize = 0;
	o.mReadIdx = 0;
	o.mWriteIdx = 0;
	o.mData = nullptr;
}

CircularBuffer::~CircularBuffer()
{
	delete[] mData;
}

CircularBuffer& CircularBuffer::operator=(const CircularBuffer& o)
{
	if (this != &o)
	{
		// By doing things this way we ensure the object stays in a valid
		// state when new throws.
		auto p = mData;
		mData = new unsigned char[o.mCapacity];
		delete[] p;

		mCapacity = o.mCapacity;
		mSize = o.mSize;
		mReadIdx = o.mReadIdx;
		mWriteIdx = o.mWriteIdx;

		memcpy(mData, o.mData, mSize);
	}

	return *this;
}

CircularBuffer& CircularBuffer::operator=(CircularBuffer&& o)
{
	if (this != &o)
	{
		delete[] mData;

		mData = o.mData;
		mCapacity = o.mCapacity;
		mSize = o.mSize;
		mReadIdx = o.mReadIdx;
		mWriteIdx = o.mWriteIdx;

		o.mData = nullptr;
		o.mCapacity = 0;
		o.mSize = 0;
		o.mReadIdx = 0;
		o.mWriteIdx = 0;
	}

	return *this;
}

size_t CircularBuffer::getCapacity() const noexcept
{
	return mCapacity;
}

size_t CircularBuffer::getSize() const noexcept
{
	return mSize;
}

size_t CircularBuffer::read(void* data, size_t max)
{
	assert(mData != nullptr);

	if (data == nullptr)
	{
		throw invalid_argument("Data is null.");
	}
	else if (max < 1 || mSize < 1)
	{
		return 0;
	}

	max = min(max, mSize);
	if (max <= mCapacity - mReadIdx)
	{
		memcpy(data, mData + mReadIdx, max);
		mReadIdx += max;
		if (mReadIdx == mCapacity)
		{
			mReadIdx = 0;
		}
	}
	else
	{
		const auto s1 = mCapacity - mReadIdx;
		memcpy(data, mData + mReadIdx, s1);
		const auto s2 = max - s1;
		memcpy(static_cast<unsigned char*>(data) + s1, mData, s2);
		mReadIdx = s2;
	}

	mSize -= max;

	return max;
}

size_t CircularBuffer::write(const void* data, size_t size)
{
	assert(mData != nullptr);

	if (data == nullptr)
	{
		throw invalid_argument("Data is null.");
	}
	else if (size < 1 || mSize == mCapacity)
	{
		return 0;
	}

	size = min(size, mCapacity - mSize);
	if (size <= mCapacity - mWriteIdx)
	{
		memcpy(mData + mWriteIdx, data, size);
		mWriteIdx += size;
		if (mWriteIdx == mCapacity)
		{
			mWriteIdx = 0;
		}
	}
	else
	{
		const auto s1 = mCapacity - mWriteIdx;
		memcpy(mData + mWriteIdx, data, s1);
		const auto s2 = size - s1;
		memcpy(mData, static_cast<const unsigned char*>(data) + s1, s2);
		mWriteIdx = s2;
	}

	mSize += size;

	return size;
}

unsigned char CircularBuffer::readByte(size_t index) const
{
	assert(mData != nullptr);

	// Index can exceed readable data if too large (i.e. index >= mSize).
	return mData[(mReadIdx + index) % mCapacity];
}

void CircularBuffer::clear()
{
	mReadIdx = 0;
	mWriteIdx = 0;
}

void CircularBuffer::discard(size_t size)
{
	size = min(size, mSize);
	if (size > 0)
	{
		mReadIdx = (mReadIdx + size) % mCapacity;
	}
}
