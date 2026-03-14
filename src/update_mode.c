#include "boot.h"

static int read_send_size(uint32_t *out_size)
{
    uint32_t size = 0U;
    const char *command = "SEND ";

    if (out_size == NULL) {
        return -1;
    }

    for (int i = 0; i < 5; ++i) {
        if (uart_getc() != command[i]) {
            return -1;
        }
    }

    while (1) {
        const char c = uart_getc();
        if (c == '\r' || c == '\n') {
            break;
        }

        if (c < '0' || c > '9') {
            return -1;
        }

        const uint32_t digit = (uint32_t)(c - '0');
        if (size > (0xFFFFFFFFU - digit) / 10U) {
            return -1;
        }

        size = (size * 10U) + digit;
    }

    *out_size = size;
    return 0;
}

int update_mode_run(void)
{
    uint32_t size = 0U;
    fw_header_t header;
    uint8_t *dest;

    bl_evt("DECISION_UPDATE");
    bl_evt("READY_FOR_UPDATE");
    bl_evt("APP_CRC_CHECK");
    uart_puts("OK\n");

    if (read_send_size(&size) != 0) {
        uart_puts("ERR: CMD\n");
        bl_evt("UPDATE_START_FAIL");
        bl_evt("APP_CRC_FAIL");
        return -1;
    }

    if (!app_image_payload_size_valid(size)) {
        uart_puts("ERR: SIZE\n");
        bl_evt("UPDATE_START_FAIL");
        bl_evt("APP_CRC_FAIL");
        return -1;
    }

    header.magic = BOOT_MAGIC;
    header.size = size;
    header.version = 1U;

    uart_puts("ERASING...\n");
    if (flash_erase_app() != 0) {
        uart_puts("ERR: ERASE\n");
        bl_evt("UPDATE_SETUP_FAIL");
        bl_evt("APP_CRC_FAIL");
        return -1;
    }

    bl_evt("READY_FOR_CHUNK");
    uart_puts("READY\n");

    dest = (uint8_t *)(APP_BASE + sizeof(fw_header_t));
    for (uint32_t i = 0U; i < size; ++i) {
        dest[i] = (uint8_t)uart_getc();
    }

    bl_evt_u32("CHUNK_OK", 0U);

    header.crc32 = crc32((const uint8_t *)(APP_BASE + sizeof(fw_header_t)), size);
    if (flash_write_header(&header) != 0) {
        uart_puts("ERR: HEADER\n");
        bl_evt("UPDATE_SETUP_FAIL");
        bl_evt("APP_CRC_FAIL");
        return -1;
    }

    bl_evt("UPDATE_SESSION_END");
    bl_evt("APP_CRC_OK");
    uart_puts("CRC?\n");
    uart_puts("OK\n");
    uart_puts("REBOOT\n");

#if PLATFORM_DIRECT_BOOT_AFTER_UPDATE
    app_image_handoff();
#else
    platform_reset();
#endif

    return 0;
}
