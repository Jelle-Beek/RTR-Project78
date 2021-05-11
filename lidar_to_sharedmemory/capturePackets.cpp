#include <pcap/pcap.h>
#include <iostream>
#include <cstdlib>

const uint8_t *header;
const uint8_t *data;
const uint8_t *tail;

uint16_t distances[360][16];
int oldAngle;

void parse_packet(uint8_t *packet) {
	int angle = ((packet[2] << 8) | (packet[3])) / 100;
	
	if(angle < oldAngle) {
		// put buffer in shared memory
	}
	
	printf("ang:%3d   ", angle);
	for(int i = 4; i < (4 + 16*3); i += 3) {
		int cm = (data[i] << 8) | (data[i+1]);
		distances[angle][(i-4)/3] = cm;
		printf("d:%4d cm   ", cm);
	}
	printf("\n");
}

void got_packet(u_char *args, const struct pcap_pkthdr *packetheader, const u_char *packet) {
	packet += 42;
	header = packet;
	data = packet + 42;
	tail = packet + 1242;
	
	for(int i = 0; i < 12; i++) {
		parse_packet((uint8_t*)(data) + i*100);
	}
	std::cout << std::endl;
}

void capturePackets_start() {
	oldAngle = 0;
	pcap_t *handle;
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
