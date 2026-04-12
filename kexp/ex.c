#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifdef USE_UTILS
#include "include/utils.h"
#define DBG_HEXDUMP(label, addr, len) hexdump((label), (addr), (len))
#else
#define DBG_HEXDUMP(label, addr, len) ((void)0)
#endif

/* Configuration */
#define DEVICE_PATH "/dev/vuln"

/* IOCTL Codes */
#define IOCTL_READ 0x1337
#define IOCTL_WRITE 0x1338

static int open_dev(const char *path, int flags) {
    int fd = open(path, flags);

    if (fd < 0) {
        fprintf(stderr, "[-] open(%s) failed: %s\n", path, strerror(errno));
        exit(EXIT_FAILURE);
    }

    return fd;
}

/* Exploit Entry */
int main(void) {
    int fd = open_dev(DEVICE_PATH, O_RDWR);

    close(fd);
    return 0;
}
