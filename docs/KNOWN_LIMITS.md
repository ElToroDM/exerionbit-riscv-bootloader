# Known Limits — RISC-V Bare-Metal Bootloader (QEMU)

**Version:** v0.1  
**Date:** 2026-02-20

---

## Target scope

- Default target is QEMU virt (RISC-V 32-bit). This is **not** a production board target.
- Real hardware ports require board-specific HAL implementation under `boards/` and
  a matching memory map in `linker/memory.ld`.

## No hardware validation

- All automated validation runs in QEMU. No physical hardware evidence is included
  in this repository.
- Visual/LED signaling is not part of this QEMU baseline.

## Update protocol scope

- The UART update protocol (115200 8N1, `BOOT?` handshake, CRC32 validation) is a
  minimal reference implementation. It is not hardened against adversarial input.
- No timeout recovery trigger or GPIO boot-mode pin is implemented in this baseline.

## Security scope

- No secure boot, image signature verification, or rollback protection is implemented.
- CRC32 provides basic integrity checking only; it is not a cryptographic primitive.
- Production hardening (signing, anti-tamper, key provisioning) is out of scope for
  this proof asset.

## Toolchain

- Built and tested with `riscv-none-elf-gcc` (xPack). Other RISC-V GCC variants
  (e.g. `riscv32-unknown-elf-gcc`) may require minor Makefile adjustments.
- Requires QEMU system emulation (`qemu-system-riscv32`) for default validation.

## Test application

- `src/test_app.c` and `src/test_app_start.S` are part of the same minimal build.
  They are validation artifacts, not a separate firmware image.

---

*For the full validation contract, see [VALIDATION_PROFILE.md](../VALIDATION_PROFILE.md) and [BOOT_SEQUENCE.md](../BOOT_SEQUENCE.md).*
