#include "boot.h"

/*
 * CRC32 (IEEE 802.3) - bitwise implementation
 *
 * Notes:
 * - Bitwise approach is compact and avoids a precomputed table to reduce
 *   flash size (trading CPU cycles for code size)
 * - We initialize to 0xFFFFFFFF and return the one's complement (~crc) to
 *   match standard CRC32 post-processing
 */

uint32_t crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320; /* polynomial */
            } else {
                crc >>= 1;
            }
        }
    }
    
    /* Finalize (XOR with 0xFFFFFFFF) */
    return ~crc;
}
