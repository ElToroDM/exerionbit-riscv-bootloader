#include "boot.h"

/*
 * UART Abstraction Layer (generic convenience wrappers)
 *
 * Responsibilities:
 * - Ensure platform is prepared before UART use
 * - Provide small helpers (puts, newline normalization) used by boot logic
 */

void uart_init(void) {
    /* Perform early platform init (clocks, power domains) first */
    platform_early_init();
    
    /* Then configure UART hardware itself */
    platform_uart_init();
}

void uart_putc(char c) {
    /* Normalize \n -> \r\n to work well with common terminals
     * (many terminals expect CR LF pair for newlines) */
    if (c == '\n') {
        platform_uart_putc('\r');
    }
    platform_uart_putc(c);
}

char uart_getc(void) {
    /* Blocking character read via platform-specific implementation */
    return platform_uart_getc();
}

void uart_puts(const char *s) {
    /* Send a NUL-terminated string using uart_putc for consistent behavior */
    while (*s) {
        uart_putc(*s++);
    }
}
