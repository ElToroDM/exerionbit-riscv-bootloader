# Professional RISC-V UART Bootloader

A minimal, robust, and portable bare-metal RISC-V bootloader designed for professional embedded systems.

## Features
- **Reliable Startup**: Assembly-based entry point with stack and BSS initialization.
- **UART Update Protocol**: Human-readable, text-based protocol for firmware updates.
- **Portability**: Isolated hardware abstraction layer (HAL) for easy porting.
- **Validation**: CRC32-based firmware validation with magic number and size checks.
- **Compact**: Designed for minimal footprint (default 64KB flash).

## Project Structure
```text
riscv-uart-bootloader/
├── src/                # Core bootloader logic (OS-agnostic)
├── include/            # Common definitions and HAL interfaces
├── linker/             # Linker scripts for memory layout
├── boards/             # Board-specific HAL implementations
│   └── qemu_virt/      # Default target: QEMU RISC-V Virt machine
├── Makefile            # Build system
└── README.md           # This document
```

## Memory Layout
The default layout is configured for the QEMU virt machine but is easily adjustable via `linker/memory.ld` and `include/boot.h`.

| Region | Address | Size | Description |
| --- | --- | --- | --- |
| **FLASH** | `0x00000000` | 64 KB | Bootloader Code |
| **APP** | `0x00010000` | 448 KB | Application Binary Partition |
| **RAM** | `0x80000000` | 128 KB | Runtime RAM (Stack, Data, BSS) |

## Update Protocol
The bootloader uses a simple UART protocol (115200 8N1).
1. **Bootloader**: Sends `BOOT?`
2. **Host**: Sends any character (e.g., `u`) to enter update mode.
3. **Bootloader**: Sends `OK`
4. **Host**: Sends `SEND <size>\n` (where `<size>` is decimal payload size)
5. **Bootloader**: Sends `READY` (after erasing flash)
6. **Host**: Sends `<raw binary data>`
7. **Bootloader**: Responds `CRC?` -> `OK` -> `REBOOT`

## Building
Requires `riscv64-unknown-elf-` toolchain.
```bash
make
```

## Running (QEMU)
```bash
make qemu
```

## Porting to New Hardware
To port the bootloader:
1. Create a new directory under `boards/<your_board>/`.
2. Implement `platform.c` providing the functions defined in `include/boot.h`.
3. Update the `Makefile` to include your board's source files.
4. (Optional) Adjust `linker/memory.ld` for your specific memory map.

## Professional Use
This code is written following C99 standards, with no dynamic allocation or interrupts, making it suitable for safety-critical or high-reliability applications where auditability is key.
