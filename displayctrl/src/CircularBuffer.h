#pragma once

#include <cstddef>

class CircularBuffer
{
public:
	explicit CircularBuffer(std::size_t capacity);
	CircularBuffer(const CircularBuffer& o);
	CircularBuffer(CircularBuffer&& o);

	~CircularBuffer();

	CircularBuffer& operator=(const CircularBuffer& o);
	CircularBuffer& operator=(CircularBuffer&& o);

	std::size_t getCapacity() const noexcept;
	std::size_t getSize() const noexcept;

	std::size_t read(void* data, std::size_t max);
	std::size_t write(const void* data, std::size_t size);

	unsigned char readByte(std::size_t index) const;

	void discard(std::size_t size);

	void clear();

private:
	std::size_t mCapacity;
	std::size_t mSize;
	std::size_t mReadIdx;
	std::size_t mWriteIdx;
	unsigned char* mData;
};
