#include "boot.h"

/* Abstraction layer for Flash operations */

int flash_write(uint32_t addr, const void *data, size_t size) {
    /* Defensive checks */
    if (addr < APP_BASE || (addr + size) > (APP_BASE + APP_MAX_SIZE)) {
        return -1;
    }
    return platform_flash_write(addr, data, size);
}

int flash_erase_app(void) {
    return platform_flash_erase(APP_BASE, APP_MAX_SIZE);
}
