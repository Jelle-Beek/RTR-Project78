#include <iostream>
#include <thread>
#include <pcap/pcap.h>
#include <fstream>
#include <cstdlib>
//#include "capturePackets.h"
#include "udpclient.h"
//#include "json.hpp"

#define HORIZONTAL_INDEX_MAX 900

//using json = nlohmann::json;
using std::to_string;

const uint8_t *header;
const uint8_t *data;
const uint8_t *tail;

uint16_t distances[HORIZONTAL_INDEX_MAX][16];
int oldAngle;

int pylonCount;
int pylonAngle[10];
int pylonDistance[10];
int horizontalIndex;

float minAngle = 0.0f, maxAngle = 360.0f;

pcap_t *handle;

void createImage() {
	int x = horizontalIndex, y = 16;
	char imgname[100];
	static int count = 0;
	printf("Writing image %d...\n", count);
	sprintf(imgname, "images/image%04d.ppm", count);
	std::ofstream image(imgname, std::ios::out);
	image << "P3\n" << x << " " << y << "\n255\n";
	for(int j = 0; j < y; j++) {
		for(int i = 0; i < x; i++) {
			int ir, ig, ib;
			ir = ig = ib = distances[i][j] * 255 / 1500;
			if(ir > 255) {ir = 255; ig = ib = 0;}
			image << ir << " " << ig << " " << ib << "\n";
		}
	}
	count++;
	image.close();
}

void detectPylons() {
	// TODO: use real data
	pylonCount = 2;
	pylonAngle[0] = 18;
	pylonDistance[0] = 180;
	pylonAngle[1] = 24;
	pylonDistance[1] = 240;
}

std::string createJson() {
	std::string json = "{";
	for(int i = 0; i < pylonCount; i++) {
		if(i > 0)
			json += ", ";
		json += to_string(i) + ": {";
		json += to_string(pylonAngle[i]);
		json += ", ";
		json += to_string(pylonDistance[i]);
		json += "}";
	}
	json += "}";
	return json;
}

void parse_partial_data(const uint8_t *packet) {
	int angle = ((packet[2] << 8) | (packet[3])) / 100;
	float exactAngle = ((float)((packet[2] << 8) | (packet[3]))) / 100.0f;
	if(exactAngle < minAngle || exactAngle > maxAngle)
		return;
	printf("Exact angle: %3.2f\n", exactAngle);
	
	if(angle < oldAngle) {
		createImage();
		detectPylons();
		horizontalIndex = 0;
		printf("%s\n", createJson().c_str());
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
	std::thread capturePackets(capturePackets_start);
	std::chrono::milliseconds timespan(5000);
	//while(1)
		std::this_thread::sleep_for(timespan);
	capturePackets_stop();
	capturePackets.join();
	return 0;
}
 
