#!/bin/bash
# buildlib.sh - Build libcam86.so directly from libcam86.c

set -e

FTDI_CFLAGS=$(pkg-config --cflags libftdi1 2>/dev/null || echo "")
FTDI_LIBS=$(pkg-config --libs libftdi1 2>/dev/null || echo "-lftdi1")

echo "Building libcam86.so..."

gcc -O2 -shared -fPIC \
    -o libcam86.so \
    libcam86.c \
    $FTDI_CFLAGS \
    $FTDI_LIBS \
    -lpthread -lm \
    -Wno-unused-variable \
    -Wno-unused-function \
    -Wno-pointer-sign \
    -include stdbool.h

echo "Done: $(ls -lh libcam86.so)"
