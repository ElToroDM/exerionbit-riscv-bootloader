# exerionbit-riscv-bootloader
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)&nbsp;&nbsp;
[![Build Status](https://github.com/ElToroDM/exerionbit-riscv-bootloader/actions/workflows/build.yml/badge.svg?style=flat-square)](https://github.com/ElToroDM/exerionbit-riscv-bootloader/actions)&nbsp;&nbsp;
[![QEMU Validated](https://img.shields.io/badge/QEMU-Validated-success?style=flat-square&logo=qemu)](https://www.qemu.org/)&nbsp;&nbsp;
[![Size ~3KB](https://img.shields.io/badge/Size-%3C3KB-blue?style=flat-square)](https://github.com/ElToroDM/exerionbit-riscv-bootloader)&nbsp;&nbsp;
[![Custom Paid Ports](https://img.shields.io/badge/Custom-Paid%20Ports-brightgreen?style=flat-square)](https://github.com/ElToroDM/exerionbit-riscv-bootloader/issues)&nbsp;&nbsp;

**Portable bare-metal RISC-V UART bootloader reference**  
Assembly entry • CRC32 validation • Portable HAL • QEMU reference for architecture review and early port de-risking

Boot flow aligned with BRS-B principles (RISC-V ecosystem, ratified 2025): minimal, standardized handoff, no heavy UEFI/ACPI stack.
Scope note: this repository demonstrates baseline alignment, not full production hardening or full standards conformance.

- This is the supporting reference architecture behind ExerionBit's public ESP32-C3 proof, not a competing front door.  
- Use it to inspect the boot path, review portability assumptions, and reduce risk before board-specific adaptation work.

This repository provides a portable QEMU-based RISC-V reference for teams that want to inspect the boot path, validation behavior, and porting assumptions before moving to board-specific implementation.

## Best fit

- Teams that want architecture review before custom-board work starts
- Buyers whose main question is portability, boot-path clarity, or de-risking assumptions
- ESP32 RISC-V teams that want to inspect the reference architecture behind the public ESP32-C3 proof

## Commercial role

Use this repository for:
- architecture de-risking review before a board-specific scope starts
- auditability discussions around explicit boot-path behavior
- clarifying what should be adapted before asking for First-Board Bring-Up or Verified Boot Gate work

If the immediate need is ESP32-C3 bring-up, start with the ESP32-C3 repository because it is the strongest public proof today. Other ESP32 RISC-V chips can still be handled as scoped follow-on work when requirements and validation targets are explicit.

## What this repository proves

- Minimal, auditable RISC-V boot path with explicit assembly-to-C startup
- Deterministic UART update baseline with CRC validation
- Reproducible protocol behavior in QEMU for early architecture validation and port de-risking

## What this repository does not prove

- Production secure boot hardening internals
- Production key lifecycle architecture
- Anti-tamper internals for adversarial environments

## Quick demo

```bash
make all
make qemu
python3 test_validator.py
```

## Need / Scope / Timeline

| Need | Typical timeline | Includes | Evidence artifact |
|---|---|---|---|
| Architecture de-risking review | 1-2 days | Deterministic protocol + CRC32 gate + logs | `docs/evidence/<release>/logs/qemu_update_protocol.log` |
| First-Board Bring-Up preparation | 3-5 days | Boot decision path + diagnostics contract + porting notes | `docs/evidence/<release>/expected-vs-observed.md` |
| Verified Boot Gate preparation | 5-10 days | Integrity/signature baseline mapping + BRS-B principles note | `docs/evidence/<release>/compliance-baseline.md` |

## Start a scoped project

Use this repository to qualify architecture questions before board-specific implementation starts.

To request a scoping pass, email `exerionbit.diego@gmail.com` with:
- target SoC or board
- current boot blocker
- desired outcome: `Architecture de-risking review`, `First-Board Bring-Up`, or `Verified Boot Gate`
- expected timeline

If the need is immediate ESP32-C3 delivery, start with the ESP32-C3 repository and use this reference as supporting architecture evidence.
Web entry point: `https://www.exerionbit.com`

## Known limits

- Default target is QEMU virt, not a specific production board
- Real hardware adaptation still requires board-specific HAL and memory map
- Visual LED contract is not part of this QEMU baseline
- This repository supports broader RISC-V review, but it does not replace the ESP32-C3 real-hardware proof surface

→ See [docs/KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md) for the full list.

## Standards alignment (baseline)

- BRS-B principles alignment: minimal boot flow, explicit handoff contract, no heavy UEFI/ACPI dependency.
- Scope note: this repository is not a full BRS/BRS-B conformance claim.
- Reference: RISC-V BRS ratification (2025), last checked 2026-03-18.

## Quick Start

**Prerequisites:**
- RISC-V toolchain (`riscv-none-elf-gcc` or equivalent)
- GNU Make
- QEMU (system emulation)

**Build and run:**
```bash
make all        # Compile bootloader
make qemu       # Run in QEMU
```

**Run automated tests:**
```bash
python3 test_validator.py    # Protocol validation test
```

**Run live visual validation (Windows PowerShell):**
```powershell
.\scripts\run-test-with-uart-tail.ps1
```

**Demo capture mode (for terminal recording/GIF preparation):**
```powershell
.\scripts\run-test-with-uart-tail.ps1 -DemoMode
```

**Expected output:** Bootloader waits for UART input, displays `BOOT?`

> 📖 **Detailed setup instructions:** See [SETUP.md](SETUP.md)

---

## Why this reference matters

- **Architecture review first**: Portable HAL + clear separation make it easier to inspect porting assumptions before touching a board-specific codebase.
- **No vendor lock-in**: 100% open-source under the MIT License; no proprietary SDKs or vendor binaries.
- **Audit and debug friendly**: Explicit C and assembly with minimal abstractions support technical review and compliance-oriented discussion.
- **QEMU proof before board scope**: Validated in QEMU virt and designed bottom-up to reduce surprises before real-hardware adaptation.
- **Owned source**: Complete source delivered so teams can audit, adapt, and carry the design forward.

Best used by small hardware teams, early-stage OEMs, and boutique engineering consultancies that want a reference architecture before committing to board-specific bring-up work.

## Features

- Reliable bare-metal startup (assembly `_start` with stack/BSS init)
- Human-readable UART update protocol (115200 8N1)
- CRC32 + magic number + size firmware validation
- Compact footprint (default ~3 KB for bootloader)
- Clean handoff to application
- Portable HAL for easy porting

## Need a Scoped Review or Port?

- Architecture de-risking review before board-specific implementation
- Preparation work before First-Board Bring-Up starts on a real target
- Recovery trigger and diagnostics contract decisions before Factory and Field Recovery work
- Verification-path discussion before a scoped Verified Boot Gate engagement
- Fast delivery once board assumptions and scope are explicit

## Memory Layout (QEMU virt default – adjustable)

| Region | Address | Size | Description |
| --- | --- | --- | --- |
| FLASH | 0x00000000 | 64 KB | Bootloader code |
| APP | 0x00010000 | 448 KB | Application binary partition |
| RAM | 0x80000000 | 128 KB | Runtime (stack, data, BSS) |

See `linker/memory.ld` and `include/boot.h` for details.

## Update Protocol (UART 115200 8N1)

1. Bootloader sends: `BOOT?`
2. Host sends any char (e.g. `u`) → enter update mode
3. Bootloader: `OK`
4. Host: `SEND <size>\n` (decimal size)
5. Bootloader: `READY` (after flash erase)
6. Host sends raw binary data
7. Bootloader: `CRC?` → `OK` → `REBOOT`

## Porting to Real Hardware

- Create `boards/<your_board>/`
- Implement `platform.c` with HAL functions from `include/boot.h` (`uart_init()`, `uart_putc()`, etc.)
- Optional: GPIO/LED init for signaling
- Adjust `linker/memory.ld` for real flash/RAM map
- Update `Makefile` for new target
- Build & flash with your target's flashing tool (OpenOCD, JLink, or equivalent)

## Status

- ✅ QEMU virt reference fully working
- ✅ Windows native support (tested)
- ✅ Linux / WSL / macOS support

📖 For detailed setup instructions and troubleshooting, see [SETUP.md](SETUP.md)

## Contact

- Request scoped architecture review or board-port de-risking work
- Email: `exerionbit.diego@gmail.com`
- Web: `https://www.exerionbit.com`
- For immediate ESP32-C3 `First-Board Bring-Up`, use the public ESP32-C3 repository as the main proof surface
- For alignment details, see `BOOT_SEQUENCE.md` and `VALIDATION_PROFILE.md`
