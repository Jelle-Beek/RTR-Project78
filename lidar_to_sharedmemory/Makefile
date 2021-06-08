FLAGS =  -Wall -std=c++11 -g -Og -Wno-unused-variable
COMPILER = g++

all:                             main.o udpclient.o
	$(COMPILER) $(FLAGS) -o main main.o udpclient.o -lpcap -lpthread
	rm images/*.ppm

main.o: main.cpp json.hpp
	$(COMPILER) $(FLAGS) -c main.cpp -o main.o

capturePackets.o: capturePackets.cpp
	$(COMPILER) $(FLAGS) -c capturePackets.cpp -o capturePackets.o -fpermissive

udpclient.o: udpclient.cpp udpclient.h
	$(COMPILER) $(FLAGS) -c udpclient.cpp -o udpclient.o

clean:
	rm main *.o
