/*
 * Professional RISC-V UART Bootloader - Assembly Entry Point
 */

.section .text.init
.global _start

_start:
    /* Disable interrupts (just in case) */
    csrci mstatus, 8

    /* Setup stack pointer */
    la sp, _stack_top

    /* Initialize Global Pointer (if used, though -ffreestanding usually avoids it) */
    .option push
    .option norelax
    la gp, __global_pointer$
    .option pop

    /* Clear BSS section */
    la a0, _bss_start
    la a1, _bss_end
    beq a0, a1, 2f
1:
    sw zero, 0(a0)
    addi a0, a0, 4
    bltu a0, a1, 1b
2:

    /* Copy data section from FLASH to RAM */
    la a0, _data_start
    la a1, _data_end
    la a2, _data_load
    beq a0, a1, 4f
3:
    lw a3, 0(a2)
    sw a3, 0(a0)
    addi a0, a0, 4
    addi a2, a2, 4
    bltu a0, a1, 3b
4:

    /* Call main() */
    call main

    /* If main returns, loop forever */
_exit:
    j _exit
