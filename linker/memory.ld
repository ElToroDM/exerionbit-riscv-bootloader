/*
 * Professional RISC-V UART Bootloader - Linker Script
 * Target: RV32IM
 */

OUTPUT_ARCH(riscv)
ENTRY(_start)

MEMORY
{
    /* Adjusted for QEMU virt machine compatibility */
    /* FLASH is simulated at the start of RAM for this demo */
    FLASH (rx)  : ORIGIN = 0x80000000, LENGTH = 64K
    APP   (rx)  : ORIGIN = 0x80010000, LENGTH = 448K
    RAM   (rwx) : ORIGIN = 0x80100000, LENGTH = 128K
}

/* Define stack top (grows downwards) */
_stack_top = ORIGIN(RAM) + LENGTH(RAM);

SECTIONS
{
    /* Global pointer for relaxation */
    . = ORIGIN(RAM);
    __global_pointer$ = . + 0x800;

    .text :
    {
        *(.text.init)    /* Entry point must be first */
        *(.text .text.*)
    } > FLASH

    .rodata :
    {
        . = ALIGN(4);
        *(.rodata .rodata.*)
        *(.srodata .srodata.*)
    } > FLASH

    .data :
    {
        . = ALIGN(4);
        _data_start = .;
        *(.data .data.*)
        *(.sdata .sdata.*)
        . = ALIGN(4);
        _data_end = .;
    } > RAM AT > FLASH

    _data_load = LOADADDR(.data);

    .bss (NOLOAD) :
    {
        . = ALIGN(4);
        _bss_start = .;
        *(.bss .bss.*)
        *(.sbss .sbss.*)
        *(COMMON)
        . = ALIGN(4);
        _bss_end = .;
    } > RAM

    /* Remove unused sections */
    /DISCARD/ :
    {
        *(.comment)
        *(.note*)
        *(.eh_frame*)
    }
}
