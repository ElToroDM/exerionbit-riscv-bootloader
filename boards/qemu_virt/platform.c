#include "boot.h"

/* 
 * QEMU Virt Platform implementation
 * UART: 16550A at 0x10000000
 */

#define UART0_BASE 0x10000000

/* Use explicit volatile cast to prevent compiler optimizations on register pooling */
#define UART_REG(r) (*(volatile uint8_t *)(UART0_BASE + (r)))

#define UART_THR 0
#define UART_RBR 0
#define UART_IER 1
#define UART_FCR 2
#define UART_LCR 3
#define UART_LSR 5

#define UART_LSR_RX_READY 0x01
#define UART_LSR_TX_IDLE  0x20

void platform_init(void) {
    /* 16550A Initializaton */
    UART_REG(UART_IER) = 0x00; /* Disable interrupts */
    UART_REG(UART_LCR) = 0x03; /* 8N1 */
    UART_REG(UART_FCR) = 0x07; /* Enable FIFO, clear TX/RX */
}

void platform_uart_putc(char c) {
    /* Wait for TX to be empty */
    while (!(UART_REG(UART_LSR) & UART_LSR_TX_IDLE));
    UART_REG(UART_THR) = (uint8_t)c;
}

char platform_uart_getc(void) {
    /* Wait for RX to be ready */
    while (!(UART_REG(UART_LSR) & UART_LSR_RX_READY));
    return (char)UART_REG(UART_RBR);
}

int platform_flash_write(uint32_t addr, const void *data, size_t size) {
    uint8_t *dest = (uint8_t *)(uintptr_t)addr;
    const uint8_t *src = (const uint8_t *)data;
    for (size_t i = 0; i < size; i++) {
        dest[i] = src[i];
    }
    return 0;
}

int platform_flash_erase(uint32_t addr, size_t size) {
    uint8_t *dest = (uint8_t *)(uintptr_t)addr;
    for (size_t i = 0; i < size; i++) {
        dest[i] = 0xFF;
    }
    return 0;
}

void platform_reset(void) {
    volatile uint32_t *test_device = (uint32_t *)0x100000;
    *test_device = 0x7777; /* QEMU poweroff/reset */
    while(1);
}
