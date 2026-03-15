/*
 * cam86_api.c
 * Thin shared-library wrapper around libcam86.c for ctypes access from Python.
 * Compile with build.sh.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "libcam86.c"

/* ------------------------------------------------------------------ */
/* Exported API                                                         */
/* ------------------------------------------------------------------ */

int cam86_connect(void)
{
    if (!cameraConnect()) return -1;

    /* Mirror cam86_ccd.cpp Connect() post-connect steps */
    cameraSetBaudrateA(BRA);        /* BRA=20, matches INDI driver */
    cameraSetBaudrateB(BRB);        /* BRB=10 for new firmware */
    usleep(500 * 1000);
    //cameraSetOffset(-20);
    //cameraSetGain(0);
    cameraSetReadingTime(1);

    /* cameraConnect() sets chunksize to 16KB internally — override to 64KB
       and latency to 1ms for maximum USB read throughput on channel A */
    cameraSetLibftdiLatA(1);
    ftdi_read_data_set_chunksize(CAM8A, 48000);
    cameraSetLibftdiTimerAR(10000);
    cameraSetLibftdiTimerAW(10000);

    return 0;
}

int cam86_disconnect(void)
{
    return cameraDisconnect() ? 0 : -1;
}

int cam86_get_firmware_version(void)
{
    Spi_comm(0xBB, 0);
    return (int)siout;
}

int cam86_get_ccd_temp_raw(void)
{
    Spi_comm(0xBF, 0);
    return (int)siout;
}

int cam86_set_gain(int val)
{
    return cameraSetGain(val) ? 0 : -1;
}

int cam86_set_offset(int val)
{
    return cameraSetOffset(val) ? 0 : -1;
}

int cam86_get_error(void)
{
    return cameraGetError();
}

void cam86_clear_errors(void)
{
    errorWriteFlag = false;
    errorReadFlag  = false;
}

void cam86_set_timer_a(int ms)
{
    cameraSetLibftdiTimerAR(ms);
    cameraSetLibftdiTimerAW(ms);
}

int cam86_get_state(void)
{
    return cameraGetCameraState();
}

int cam86_start_exposure(int bin, int start_x, int start_y,
                         int num_x, int num_y,
                         double duration, int light)
{
    return cameraStartExposure(bin, start_x, start_y,
                               num_x, num_y,
                               duration, (bool)light);
}

int cam86_stop_exposure(void)
{
    return cameraStopExposure() ? 0 : -1;
}

int cam86_image_ready(void)
{
    return cameraGetImageReady() ? 1 : 0;
}

int cam86_get_image(uint16_t *buf, int width, int height,
                    int start_x, int start_y, int bin)
{
    if (!buf) return -1;
    int i, j;
    uint16_t pix;
    if (bin == 0) {
        for (j = start_y; j < height + start_y; j++)
            for (i = start_x; i < start_x + width; i++) {
                pix = cameraGetImageXY(i, j);
                buf[(j - start_y) * width + (i - start_x)] = (pix >> 8) | (pix << 8);
            }
    } else {
        for (j = 0; j < height; j++)
            for (i = 0; i < width; i++) {
                pix = cameraGetImageXY(2*i, 2*j);
                buf[j * width + i] = (pix >> 8) | (pix << 8);
            }
    }
    return width * height;
}

int cam86_get_width(void)  { return CameraWidth; }
int cam86_get_height(void) { return CameraHeight; }

int cam86_spi_comm(uint8_t cmd, uint16_t param)
{
    Spi_comm(cmd, param);
    return (int)siout;
}
