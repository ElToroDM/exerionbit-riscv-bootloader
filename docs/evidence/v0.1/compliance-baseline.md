# Compliance Baseline — RISC-V Bare-Metal Bootloader

**Version:** v0.1  
**Date:** 2026-03-23

---

## Purpose

This note captures the compliance-ready baseline documented by this QEMU RISC-V bootloader repository.
It is intentionally narrow: reproducible protocol behavior, explicit handoff, and a visible
security contact path. It is not a claim of full production hardening.

## Scope

Included in this repository baseline:
- deterministic UART update protocol behavior in QEMU
- baseline integrity checking with CRC32
- reproducible evidence artifacts for normal/update/recovery paths
- BRS-B principles alignment wording with an explicit non-conformance note

Out of scope:
- advanced production hardening internals
- full key lifecycle architecture
- anti-tamper implementation details
- authenticated image signing or encryption in this repository baseline
- real hardware validation

## Baseline assumptions

- QEMU virt is the supported validation target.
- No physical hardware evidence is included in this repository baseline.
- CRC32 is used for integrity checking only.
- Advanced platform security features are outside the scope of this repository evidence set.
- Production hardening is intentionally excluded from this repository.

## Vulnerability handling path

For non-sensitive issues:
- open a GitHub issue in this repository with prefix `[SECURITY]`
- include reproduction steps, expected behavior, observed behavior, and environment details

For potentially sensitive findings:
- do not post exploit details publicly
- open a brief contact request via GitHub issue without exploit details
- request a secure follow-up channel

## Support window

Support in this repository is limited to:
- reproducibility issues in documented setup and validation paths
- correctness issues in published baseline behavior

Separate project scopes can define explicit response windows and acceptance criteria.

## Known limits

- Default target is QEMU virt, not a production board.
- No physical hardware validation is included.
- No secure boot, rollback protection, or signing is included.
- No LED or other hardware signaling is part of the baseline.
- Production hardening and board-specific adaptation are intentionally out of scope.

See [docs/KNOWN_LIMITS.md](../../KNOWN_LIMITS.md) for the full limit set.

## BRS-B conformance note

This asset is aligned with BRS-B principles: minimal boot path, explicit handoff, and no heavy UEFI/ACPI dependency.
That wording is a baseline alignment statement, not a full BRS/BRS-B conformance claim.

Reference source and last checked date:
- RISC-V BRS ratification (2025)
- last checked: 2026-03-18

## Evidence mapping

This baseline is supported by the repository documentation and evidence set:
- [README.md](../../../README.md)
- [SECURITY.md](../../../SECURITY.md)
- [BOOT_SEQUENCE.md](../../../BOOT_SEQUENCE.md)
- [VALIDATION_PROFILE.md](../../../VALIDATION_PROFILE.md)
- [docs/KNOWN_LIMITS.md](../../KNOWN_LIMITS.md)
- [docs/evidence/v0.1/expected-vs-observed.md](expected-vs-observed.md)

---

*This note describes the documented repository baseline. Production hardening is outside the scope of this note.*
