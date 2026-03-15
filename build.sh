#!/bin/bash
# build.sh - builds both cam86_api.so and libcam86.so

set -e

FTDI_CFLAGS=$(pkg-config --cflags libftdi1 2>/dev/null || echo "")
FTDI_LIBS=$(pkg-config --libs libftdi1 2>/dev/null || echo "-lftdi1")
WARN="-Wno-unused-variable -Wno-unused-function -Wno-pointer-sign -Wno-deprecated-declarations"

echo "Building cam86_api.so..."
gcc -O2 -shared -fPIC -o cam86_api.so cam86_api.c \
    $FTDI_CFLAGS $FTDI_LIBS -lpthread -lm $WARN
echo "  $(ls -lh cam86_api.so)"

echo "Building libcam86.so..."
gcc -O2 -shared -fPIC -o libcam86.so libcam86.c \
    $FTDI_CFLAGS $FTDI_LIBS -lpthread -lm -include stdbool.h $WARN
echo "  $(ls -lh libcam86.so)"

echo "Done."
