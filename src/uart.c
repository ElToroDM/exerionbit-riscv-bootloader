#include "boot.h"

/* Wrapper for platform-specific UART */

void uart_init(void) {
    platform_init();
}

void uart_putc(char c) {
    if (c == '\n') {
        platform_uart_putc('\r');
    }
    platform_uart_putc(c);
}

char uart_getc(void) {
    return platform_uart_getc();
}

void uart_puts(const char *s) {
    while (*s) {
        uart_putc(*s++);
    }
}
