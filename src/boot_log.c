#include "boot.h"

static void uart_put_u32_dec(uint32_t value)
{
    char buffer[11];
    int index = 0;

    if (value == 0U) {
        uart_putc('0');
        return;
    }

    while (value > 0U && index < (int)sizeof(buffer)) {
        buffer[index++] = (char)('0' + (value % 10U));
        value /= 10U;
    }

    while (index > 0) {
        uart_putc(buffer[--index]);
    }
}

void bl_evt(const char *token)
{
    uart_puts("BL_EVT:");
    uart_puts(token);
    uart_puts("\n");
}

void bl_evt_u32(const char *token, uint32_t value)
{
    uart_puts("BL_EVT:");
    uart_puts(token);
    uart_puts(":");
    uart_put_u32_dec(value);
    uart_puts("\n");
}
