FLAGS =  -Wall -std=c++11 -g -Og -Wno-unused-variable
COMPILER = g++

all:                             main.o capturePackets.o
	$(COMPILER) $(FLAGS) -o main main.o capturePackets.o -lpcap -lpthread

main.o: main.cpp
	$(COMPILER) $(FLAGS) -c main.cpp -o main.o

capturePackets.o: capturePackets.cpp
	$(COMPILER) $(FLAGS) -c capturePackets.cpp -o capturePackets.o -fpermissive

clean:
	rm main *.o
