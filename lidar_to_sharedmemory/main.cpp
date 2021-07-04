/*
 * Henkjan Veldhoven - 0975269@hr.nl
 * If you're working on Project 56, feel free to send me an email. This code
 * needs some explanation and I want to help you to get started.
 */

#include <iostream>
#include <thread>
#include <pcap/pcap.h>
#include <fstream>
#include <cstdlib>
//#include "capturePackets.h"
#include "udpclient.h"
//#include "json.hpp"
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <iostream>
#include <fcntl.h>
#include <stdlib.h>

#define HORIZONTAL_INDEX_MAX 900

//using json = nlohmann::json;
using std::to_string;

const uint8_t *header;
const uint8_t *data;
const uint8_t *tail;

uint16_t distances[HORIZONTAL_INDEX_MAX][16];
uint16_t convolution[HORIZONTAL_INDEX_MAX][16];
int oldAngle;

int pylonCount;
int pylonAngle[10];
int pylonDistance[10];
int horizontalIndex;

float minAngle = 0.0f, maxAngle = 360.0f;

pcap_t *handle;
int fd;
size_t pagesize;
char* region;

void createImage() {
	int x = horizontalIndex, y = 16;
	char imgname[100];
	static int count = 0;
	printf("Writing image %d...\n", count);
	sprintf(imgname, "images/image%04d.ppm", 0);
	std::ofstream image(imgname, std::ios::out);
	image << "P3\n" << x << " " << y << "\n255\n";
	for(int j = y - 1; j >= 0; j--) {
		for(int i = 0; i < x; i++) {
			int ir, ig, ib;
			ir = ig = ib = distances[i][j] * 255 / 300; // 300 cm
			if(ir > 255) {ir = 255; ig = ib = 0;}
			image << ir << " " << ig << " " << ib << "\n";
		}
	}
	count++;
	image.close();
}

void createConvolutionImage() {
	int x = horizontalIndex, y = 16;
	char imgname[100];
	static int count = 0;
	printf("Writing convolution image %d...\n", count);
	sprintf(imgname, "images/image%04d_conv.ppm", count);
	std::ofstream image(imgname, std::ios::out);
	image << "P3\n" << x << " " << y << "\n255\n";
	for(int j = 0; j < y; j++) {
		for(int i = 0; i < x; i++) {
			int ir, ig, ib;
			ir = ig = ib = convolution[i][j];
			//if(ir > 255) {ir = 255; ig = ib = 0;}
			image << ir << " " << ig << " " << ib << "\n";
		}
	}
	count++;
	image.close();
}

void detectPylons() {
	// TODO: use real data
	pylonCount = 4;
	pylonAngle[0] = 18;
	pylonDistance[0] = 180;
	pylonAngle[1] = 24;
	pylonDistance[1] = 240;
	pylonAngle[2] = 28;
	pylonDistance[2] = 280;
	pylonAngle[3] = 32;
	pylonDistance[3] = 320;
	int convolution_coeffs[19*2+1];
	for(int i = -19; i < 20; i++)
		convolution_coeffs[i] = 1;
	convolution_coeffs[18] = 0;
	convolution_coeffs[19] = 100;
	convolution_coeffs[20] = 0;
	
	// test data
	for(int x = 0; x < horizontalIndex; x++) {
		distances[x][0] = 1000;
	}
	distances[100][0] = 900;
	
	
	for(int y = 0; y < 16; y++) {
		for(int x = 0; x < horizontalIndex; x++) {
			int avg = 0;
			for(int pos = -19; pos < 20; pos++) {
				avg += distances[(x + pos + horizontalIndex)%horizontalIndex][y];
			}
			avg /= (19*2+1);
			int conv = 0;
			for(int pos = -19; pos < 20; pos++) {
				conv += convolution_coeffs[pos+19] * (distances[(x + pos + horizontalIndex)%horizontalIndex][y]);
			}
			//avg /= (19*2+1);
			// avg is now average distance in cm. Scale to 0-255.
			//avg /= 4; // max distance is about 10m
			//if(avg > 255) avg = 0;
			//convolution[x][y] = avg;
			//conv *= -1;
			if(conv < 0) conv = 0;
			conv /= 800;
			if(conv > 255) conv = 255;
			convolution[x][y] = conv;
		}
	}
}

std::string createJson() {
	std::string json = "{";
	for(int i = 0; i < pylonCount; i++) {
		json += to_string(pylonAngle[i]);
		json += ":";
		json += to_string(pylonDistance[i]);
		if(i+1 < pylonCount)
			json += ", ";
	}
	json += "}";
	printf("%s\n", json.c_str());
	return json;
}

void parse_partial_data(const uint8_t *packet) {
	int angle = ((packet[2] << 8) | (packet[3])) / 100;
	float exactAngle = ((float)((packet[2] << 8) | (packet[3]))) / 100.0f;
	if(exactAngle < minAngle || exactAngle > maxAngle)
		return;
	printf("Exact angle: %3.2f\n", exactAngle);
	
	static int skip = 0;
	if(angle < oldAngle) {
		if(skip++ % 10 == 0)
			createImage();
		detectPylons();
		//createConvolutionImage();
		horizontalIndex = 0;
		char json[80];
		strcpy(json, createJson().c_str());
		//strcpy(region, json);
		region[0] = 'a';
		region[1] = 'a';
		region[2] = 'a';
		region[3] = 'a';
		region[4] = 'b';
		region[5] = 'b';
		region[6] = 'b';
		region[7] = 'b';
		region[8] = 'c';
		region[12] = 'd';
		
		//printf("%s\n", json);
	}
	oldAngle = angle;
	printf("%d th horizontalIndex\n", horizontalIndex);
	//printf("ang:%3d   ", angle);
	for(int i = 0; i < 32; i++) {
		if(i == 16)
			horizontalIndex++;
		if(horizontalIndex >= HORIZONTAL_INDEX_MAX)
			break;
		int cm = (packet[4+i*3] << 8) | (packet[5+i*3]);
		distances[horizontalIndex][i%16] = cm;
		//printf("d:%5d cm ", distances[angle][(i-4)/3]);
	}
	horizontalIndex++;
	//printf("\n");
}

void got_packet(u_char *args, const struct pcap_pkthdr *packetheader, const u_char *packet) {
	packet += 42;
	header = packet;
	data = packet + 42;
	tail = packet + 1242;
	//uint8_t data_local[1200];
	//memcpy(data_local, data, 1200);
	for(int i = 0; i < 12; i++) {
		parse_partial_data(&data[i*100]);
	}
	//std::cout << std::endl;
}

void capturePackets_start() {
	oldAngle = 0;
	horizontalIndex = 0;
	char dev[] = "enp3s0";
	char errbuf[PCAP_ERRBUF_SIZE];
	struct bpf_program fp;
	char filter_exp[] = "port 6699 and udp";
	bpf_u_int32 mask;
	bpf_u_int32 net;
	struct pcap_pkthdr header;
	u_char const *packet;
	
	if(pcap_lookupnet(dev, &net, &mask, errbuf) == -1) {
		std::cout << "Can't get netmask for device " << dev << std::endl;
		net = 0;
		mask = 0;
	}
	handle = pcap_open_live(dev, BUFSIZ, 0, 1000, errbuf);
	if(handle == NULL) {
		std::cout << "Couldn't open device " << dev << ": " << errbuf << std::endl;
		exit(-1);
	}
	if(pcap_compile(handle, &fp, filter_exp, 0, net) == -1) {
		std::cout << "Couldn't parse filter " << filter_exp << ": " << pcap_geterr(handle) << std::endl;
		exit(-2);
	}
	if(pcap_setfilter(handle, &fp) == -1) {
		std::cout << "Couldn't install filter " << filter_exp << ": " << pcap_geterr(handle) << std::endl;
		exit(-3);
	}
	// grab a packet
	pcap_loop(handle, 0, got_packet, NULL);
	pcap_close(handle);
}

void capturePackets_stop() {
	pcap_breakloop(handle);
}

int main(int argc, char **argv) {
	pagesize = getpagesize();
	if ((fd = open("pods.txt", O_RDWR, 0)) == -1) {
		printf("unable to open pods.txt\n");
		return 0;
	}
	// open the file in shared memory
	region = (char*) mmap(NULL, pagesize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
	if(region == MAP_FAILED) {
		printf("MAP_FAILED\n");
		return 0;
	}
	close(fd);
	//write(region, "Helloasd", 5);
	int x=0;
	
	/*while(true) {
		std::cout << "Input 5 to stop:";
		std::cin>> x;
		std::cout<<"Value of x:"<<x<<std::endl;
		strcpy(region, std::to_string(x).c_str());
		if (x % 5 == 0)
			break;
	}*/
	printf("Contents of region: %s\n", region);
	std::thread capturePackets(capturePackets_start);
	std::chrono::milliseconds timespan(8000);
	while(1)
		std::this_thread::sleep_for(timespan);
	capturePackets_stop();
	capturePackets.join();

	int unmap_result = munmap(region, 1 << 10);
	if (unmap_result != 0) {
		perror("Could not munmap");
		return 1;
	}
	return 0;
}
 
