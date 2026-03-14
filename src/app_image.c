#include "boot.h"

int app_image_payload_size_valid(uint32_t payload_size)
{
    if (payload_size == 0U || payload_size > APP_PAYLOAD_MAX_SIZE) {
        return 0;
    }

    return 1;
}

int app_image_validate(void)
{
    const fw_header_t *header = (const fw_header_t *)APP_BASE;

    if (header->magic != BOOT_MAGIC) {
        return -1;
    }

    if (!app_image_payload_size_valid(header->size)) {
        return -1;
    }

    const uint32_t calculated_crc = crc32((const uint8_t *)(APP_BASE + sizeof(fw_header_t)), header->size);
    if (calculated_crc != header->crc32) {
        return -1;
    }

    return 0;
}

void app_image_handoff(void)
{
    bl_evt("LOAD_APP");
    bl_evt("HANDOFF");
    uart_puts("Jumping to application...\n");
    uart_puts("APP_HANDOFF\n");
    bl_evt("HANDOFF_APP");

    void (*app_entry)(void) = (void (*)(void))(APP_BASE + sizeof(fw_header_t));
    app_entry();
}
