#!/usr/bin/env python3
"""
cam86_capture.py — check firmware version, take 100ms exposure, save image.
Requires cam86_api.so built from cam86_api.c + updated libcam86.c.
"""

import ctypes, os, sys, time
import numpy as np

HERE    = os.path.dirname(os.path.abspath(__file__))
lib     = ctypes.CDLL(os.path.join(HERE, "cam86_api.so"))

lib.cam86_connect.restype          = ctypes.c_int
lib.cam86_disconnect.restype       = ctypes.c_int
lib.cam86_get_firmware_version.restype = ctypes.c_int
lib.cam86_get_ccd_temp_raw.restype = ctypes.c_int
lib.cam86_clear_errors.restype     = None
lib.cam86_start_exposure.restype   = ctypes.c_int
lib.cam86_start_exposure.argtypes  = [
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
    ctypes.c_double, ctypes.c_int,
]
lib.cam86_image_ready.restype      = ctypes.c_int
lib.cam86_get_image.restype        = ctypes.c_int
lib.cam86_get_image.argtypes       = [
    ctypes.POINTER(ctypes.c_uint16),
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int,
]
lib.cam86_get_width.restype        = ctypes.c_int
lib.cam86_get_height.restype       = ctypes.c_int

WIDTH    = 3000
HEIGHT   = 2000
EXPOSURE = 0.1    # seconds
BIN      = 1      # 0=no binning, 1=2x2

# Get the current nice value
# of the process
#niceValue = os.nice(0)

# Print the current nice value 
# of the process
#print("Current nice value of the process:", niceValue)

# Increase the niceness 
# of the process
#value = -20
#niceValue = os.nice(value)

# Print the current nice value 
# of the process
#print("\nCurrent nice value of the process:", niceValue)

# ── Connect ───────────────────────────────────────────────────────────────────
print("Connecting...")
if lib.cam86_connect() != 0:
    raise SystemExit("connect failed")
time.sleep(1.0)
lib.cam86_clear_errors()

# ── Firmware version ──────────────────────────────────────────────────────────
ver = lib.cam86_get_firmware_version()
print(f"Firmware version : {ver}")
if ver != 32:
    lib.cam86_disconnect()
    raise SystemExit(f"Expected firmware 32, got {ver}")

# ── Temperature ───────────────────────────────────────────────────────────────
raw  = lib.cam86_get_ccd_temp_raw()
print(f"CCD temp         : {(raw - 1280) / 10.0:.1f} °C")

# ── Expose ────────────────────────────────────────────────────────────────────
print(f"Starting {EXPOSURE*1000:.0f}ms exposure...")
lib.cam86_start_exposure(BIN, 0, 0, WIDTH, HEIGHT, EXPOSURE, 1)

deadline = time.monotonic() + 6.0
while not lib.cam86_image_ready():
    if time.monotonic() > deadline:
        lib.cam86_disconnect()
        raise SystemExit("Timed out waiting for image")
    time.sleep(0.5)

# ── Read image via C ──────────────────────────────────────────────────────────
print("Reading image...")
img = np.zeros(WIDTH * HEIGHT, dtype=np.uint16)
ptr = img.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16))
n   = lib.cam86_get_image(ptr, WIDTH, HEIGHT, 0, 0, BIN)
if n < 0:
    lib.cam86_disconnect()
    raise SystemExit("cam86_get_image failed")
img = img.reshape((HEIGHT, WIDTH))
print(f"Shape : {img.shape}  dtype: {img.dtype}")
print(f"min={img.min()}  max={img.max()}  mean={img.mean():.1f}")

# ── Save ──────────────────────────────────────────────────────────────────────
try:
    from astropy.io import fits
    fname = os.path.join(HERE, "cam86_image_2x2.fits")
    hdu = fits.PrimaryHDU(img)
    hdu.header["INSTRUME"] = "Cam86"
    hdu.header["EXPTIME"]  = EXPOSURE
    hdu.header["BINNING"]  = BIN
    hdu.header["FWVER"]    = ver
    hdu.writeto(fname, overwrite=True)
except ImportError:
    fname = os.path.join(HERE, "cam86_image.npy")
    np.save(fname, img)

print(f"Saved {fname}")
lib.cam86_disconnect()
