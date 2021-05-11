#include <iostream>
#include <thread>
#include "capturePackets.h"


int main(int argc, char **argv) {
	std::thread capturePackets(capturePackets_start);
	while(1);
	
	capturePackets.join();
	return 0;
}
 
