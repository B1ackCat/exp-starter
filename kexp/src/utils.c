#include "../include/utils.h"

#include <ctype.h>
#include <stdint.h>
#include <stdio.h>

/* Print a hex dump of memory (with ASCII) */
void hexdump(const char *label, const void *addr, size_t len) {
    const uint8_t *bytes = (const uint8_t *)addr;
    const uint64_t *qwords = (const uint64_t *)addr;
    size_t qword_len = len / 8;

    puts("\n------------------------hexdump------------------------");
    printf("[DEBUG] %s (%zu bytes @ %p):\n\n", label, len, addr);

    // BYTE VIEW + ASCII
    puts("[BYTE VIEW]");
    for (size_t i = 0; i < len; i += 16) {
        printf("%02zu:%04zx│ ", i / 16, i);

        // hex part
        for (size_t j = 0; j < 16; ++j) {
            if (i + j < len)
                printf("%02x ", bytes[i + j]);
            else
                printf("   ");
        }

        printf("│ ");

        // ascii part
        for (size_t j = 0; j < 16; ++j) {
            if (i + j < len) {
                unsigned char c = bytes[i + j];
                printf("%c", isprint(c) ? c : '.');
            } else {
                printf(" ");
            }
        }

        putchar('\n');
    }

    // QWORD VIEW
    puts("\n[QWORD VIEW]");
    for (size_t i = 0; i < qword_len; i += 2) {
        size_t offset = i * 8;
        printf("%02zu:%04zx│  0x%016lx", i / 2, offset, qwords[i]);
        if (i + 1 < qword_len)
            printf("  0x%016lx", qwords[i + 1]);
        putchar('\n');
    }

    // Tail
    size_t tail_offset = qword_len * 8;
    size_t tail_len = len - tail_offset;
    if (tail_len > 0) {
        printf("[TAIL %04zx│ ", tail_offset);
        for (size_t i = 0; i < tail_len; ++i)
            printf("%02x ", bytes[tail_offset + i]);
        printf("│ ");
        for (size_t i = 0; i < tail_len; ++i) {
            unsigned char c = bytes[tail_offset + i];
            printf("%c", isprint(c) ? c : '.');
        }
        putchar('\n');
    }

    puts("------------------------hexdump------------------------\n");
}
