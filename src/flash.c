#include "boot.h"

/*
 * Flash Abstraction Layer
 *
 * Purpose: Provide simple, safe operations used by the bootloader while
 * protecting the bootloader and enforcing partition bounds.
 */

int flash_write(uint32_t addr, const void *data, size_t size) {
    /* Ensure the write stays within the application partition bounds */
    if (addr < APP_BASE || (addr + size) > (APP_BASE + APP_MAX_SIZE)) {
        return -1;
    }
    
    /* Delegate to the platform-specific flash write implementation */
    return platform_flash_write(addr, data, size);
}

int flash_erase_app(void) {
    /* Erase the entire application partition (may take time on real flash) */
    return platform_flash_erase(APP_BASE, APP_MAX_SIZE);
}

int flash_write_header(const fw_header_t *header) {
    /*
     * Write firmware header to the beginning of APP partition as the final
     * step of a successful update. Writing the header last signals a valid
     * firmware image to the bootloader on next boot (atomicity goal).
     */
    return platform_flash_write(APP_BASE, header, sizeof(fw_header_t));
}
