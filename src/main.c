#include "boot.h"

static void print_banner(void) {
    /* Small human-friendly banner printed at boot */
    uart_puts("======================================\n");
    uart_puts("   Professional RISC-V Bootloader    \n");
    uart_puts("   Target: " PLATFORM_NAME "        \n");
    uart_puts("======================================\n");
}

int main(void) {
    uart_init();
    bl_evt("INIT");
    print_banner();
    bl_evt("HW_READY");

    uart_puts("BOOT?\n");
    
    /* Wait for user decision. Echo character to improve UX over serial. */
    while(1) {
        char choice = uart_getc();
        uart_putc(choice); /* Echo for visibility */
        if (choice != '\r' && choice != '\n') {
            uart_puts("\n");
        }

        if (choice == 'u' || choice == 'U') {
            if (update_mode_run() == 0) {
                return 0;
            }

            bl_evt("DECISION_RECOVERY");
            uart_puts("Recovery Loop: Update failed. Press 'u' to retry.\n");
            while (1) {
                char retry = uart_getc();
                if (retry == 'u' || retry == 'U') {
                    update_mode_run();
                }
            }
        } else if (choice == '\r' || choice == '\n') {
            break;
        } else {
            break;
        }
    }

    bl_evt("DECISION_NORMAL");
    bl_evt("APP_CRC_CHECK");
    if (app_image_validate() == 0) {
        bl_evt("APP_CRC_OK");
        app_image_handoff();
    } else {
        bl_evt("APP_CRC_FAIL");
        bl_evt("DECISION_RECOVERY");
        uart_puts("Recovery Loop: No valid app found. Press 'u' to update.\n");
        while(1) {
            char recovery_cmd = uart_getc();
            if (recovery_cmd == 'u' || recovery_cmd == 'U') {
                update_mode_run();
            }
        }
    }

    return 0;
}
