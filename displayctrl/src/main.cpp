#include "SerialPort.h"
#include "PacketReaderTask.h"
#include "Utils.h"
#include <exception>
#include <iostream>
#include <iomanip>

using namespace std;

static void packetHandler(const Packet& pk)
{
	cout << "Packet received: " << pk.size() << endl;

	for (const auto c : pk)
	{
		cout << hex << static_cast<int>(c) << " ";
	}

	cout << endl << endl;
}

int main(int argc, char* argv[])
{
	if (argc < 2)
	{
		cerr << "Missing argument: file name" << endl;
		return EXIT_FAILURE;
	}

	try
	{
		auto sp = make_shared<SerialPort>(argv[1]);
		PacketReaderTask task(sp, packetHandler);
		task.run();
	}
	catch (const exception& ex)
	{
		cerr << "Fatal: " << ex.what() << endl;
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}
