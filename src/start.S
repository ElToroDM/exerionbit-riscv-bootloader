/*
 * Professional RISC-V UART Bootloader - Assembly Entry Point
 *
 * Purpose:
 * - Minimal, explicit startup to prepare the C runtime environment
 * - Setup stack and global pointer, clear BSS, copy initialized .data
 * - Call the C entry point `main` and never return
 *
 * Notes:
 * - Keeps the sequence small and auditable for security reviews
 * - Depends on linker-provided symbols: _stack_top, _bss_start/_bss_end,
 *   _data_start/_data_end/_data_load
 */

.section .text.init
.global _start

_start:
    /* Disable machine interrupts (clear MIE) to avoid unexpected traps */
    csrci mstatus, 8

    /* Load stack pointer from linker symbol (top of RAM stack) */
    la sp, _stack_top

    /* Initialize Global Pointer (GP) conservatively for code that may use it */
    .option push
    .option norelax
    la gp, __global_pointer$
    .option pop

    /* ---------------------------
     * Zero BSS (uninitialized data)
     * ---------------------------
     * a0 = current address, a1 = end address (exclusive)
     * This loop writes 0 words until the entire BSS is cleared.
     */
    la a0, _bss_start
    la a1, _bss_end
    beq a0, a1, 2f        // if empty, skip zeroing
1:
    sw zero, 0(a0)        // store 0 at *a0
    addi a0, a0, 4        // advance by 4 bytes (word size)
    bltu a0, a1, 1b       // continue while a0 < a1
2:

    /* -----------------------------------------------
     * Copy .data from flash (load address) into RAM
     * -----------------------------------------------
     * a2 = source (flash/ROM), a0 = destination (RAM)
     */
    la a0, _data_start
    la a1, _data_end
    la a2, _data_load
    beq a0, a1, 4f        // no initialized data to copy
3:
    lw a3, 0(a2)          // load word from source
    sw a3, 0(a0)          // store word into destination
    addi a0, a0, 4
    addi a2, a2, 4
    bltu a0, a1, 3b
4:

    /* Call the C runtime entry point. main() follows the standard ABI. */
    call main

    /* If main ever returns, stay here forever (firmware should not return) */
_exit:
    j _exit
