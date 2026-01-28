#ifndef BOOT_H
#define BOOT_H

#include <stdint.h>
#include <stddef.h>

/* Bootloader Configuration (Adjusted for QEMU Virt) */
#define BOOT_MAGIC          0x5256424C /* "RVBL" */
#define FLASH_BASE          0x80000000
#define APP_BASE            0x80010000
#define FLASH_SIZE          (64 * 1024)
#define APP_MAX_SIZE        (448 * 1024)

/* Firmware Header */
typedef struct {
    uint32_t magic;         /* Must be BOOT_MAGIC */
    uint32_t size;          /* Body size in bytes */
    uint32_t crc32;         /* CRC32 of the body */
    uint32_t version;       /* Firmware version */
} fw_header_t;

/* Platform Interface (to be implemented in boards/) */
void platform_init(void);
void platform_uart_putc(char c);
char platform_uart_getc(void);
int  platform_flash_write(uint32_t addr, const void *data, size_t size);
int  platform_flash_erase(uint32_t addr, size_t size);
void platform_reset(void);

/* Generic UART functions */
void uart_init(void);
void uart_putc(char c);
char uart_getc(void);
void uart_puts(const char *s);

/* CRC32 function */
uint32_t crc32(const uint8_t *data, size_t len);

/* Helper macros */
#define UNUSED(x) (void)(x)

#endif /* BOOT_H */
