#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <iostream>
#include <fcntl.h>
#include <stdlib.h>


int main(void) {
  size_t pagesize = getpagesize();

  
  /*
  char * region = (char *)mmap(
    //(void*) (pagesize * (1 << 20)),   // Map from the start of the 2^20th page
    NULL,
    pagesize,                         // for one page length
    PROT_READ|PROT_WRITE|PROT_EXEC,
    MAP_ANON|MAP_PRIVATE,             // to a private block of hardware memory
    0,
    0
  );
  if (region == MAP_FAILED) {
    perror("Could not mmap");
    return 1;
  }*/

  int fd = -1;
  if ((fd = open("pods.txt", O_RDWR, 0)) == -1)
     {
     printf("unable to open pods.txt\n");
     return 0;
     }
  // open the file in shared memory
  char* region = (char*) mmap(NULL, pagesize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

  strcpy(region, "Helloasd");

  int x=0;
  while(true) {
    std::cout << "Input 5 to stop:";
    std::cin>> x;
    std::cout<<"Value of x:"<<x<<std::endl;
    strcpy(region, std::to_string(x).c_str());
    if (x % 5 == 0)
      break;
  }

  printf("Contents of region: %s\n", region);

  int unmap_result = munmap(region, 1 << 10);
  if (unmap_result != 0) {
    perror("Could not munmap");
    return 1;
  }
  close(fd);
  // getpagesize
  return 0;
}