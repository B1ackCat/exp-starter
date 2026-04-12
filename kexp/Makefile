CC ?= gcc
CFLAGS ?= -Wall -Wextra -std=c11

TARGET := ex
DEBUG_TARGET := ex_dbg

.PHONY: all help release debug static clean

all: release

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  help     Show this help message"
	@echo "  release  Build release binary ($(TARGET))"
	@echo "  debug    Build debug binary with utils ($(DEBUG_TARGET))"
	@echo "  static   Build static release binary ($(TARGET))"
	@echo "  clean    Remove built binaries"

release: $(TARGET)

debug: $(DEBUG_TARGET)

static:
	$(CC) $(CFLAGS) -static ex.c -o $(TARGET)

$(TARGET): ex.c
	$(CC) $(CFLAGS) ex.c -o $(TARGET)

$(DEBUG_TARGET): ex.c src/utils.c include/utils.h
	$(CC) $(CFLAGS) -DUSE_UTILS ex.c src/utils.c -o $(DEBUG_TARGET)

clean:
	rm -f $(TARGET) $(DEBUG_TARGET)
