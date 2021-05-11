#include <pcap/pcap.h>
#include <iostream>
#include <cstdlib>

const uint8_t *header;
const uint8_t *data;
const uint8_t *tail;

void got_packet(u_char *args, const struct pcap_pkthdr *packetheader, const u_char *packet) {
	std::cout << "["<<0<<"]: ";
	packet += 42;
	header = packet;
	data = packet + 42;
	tail = packet + 1242;
	for(int i = 0; i < 8; i++) {
		printf("%02x ", data[i]);
	}
	std::cout << std::endl;
}

void capturePackets_start() {
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
