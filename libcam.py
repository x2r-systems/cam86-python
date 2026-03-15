#!/usr/bin/env python3
"""
cam86_info.py — read firmware version and temperature via libcam86.so
"""

import ctypes, os, time

lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libcam86.so"))

lib.cameraConnect.restype    = ctypes.c_bool
lib.cameraDisconnect.restype = ctypes.c_bool
lib.Spi_comm.restype         = None
lib.Spi_comm.argtypes        = [ctypes.c_uint8, ctypes.c_uint16]
lib.CameraGetTemp.restype    = ctypes.c_float

# Access siout directly — it's a global uint16_t in libcam86.c
siout = ctypes.c_uint16.in_dll(lib, "siout")

if not lib.cameraConnect():
    raise SystemExit("connect failed")
time.sleep(1.0)

lib.Spi_comm(0xBB, 0)
ver = siout.value

lib.Spi_comm(0xBF, 0)
temp_raw = siout.value
temp_c   = (temp_raw - 1280) / 10.0

print(f"Firmware version : {ver}")
print(f"CCD temp raw     : {temp_raw}  ({temp_c:.1f} °C)")

lib.cameraDisconnect()
