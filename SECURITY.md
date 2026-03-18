# Security Policy

## Scope

This public repository provides a minimal, reproducible RISC-V bootloader baseline validated in QEMU.

**Standards note:** this asset is aligned with BRS-B principles (minimal boot path, explicit handoff, no heavy UEFI/ACPI dependency), but it is not a full BRS/BRS-B conformance claim.

Included in scope:
- deterministic UART update protocol behavior and CRC32 validation
- reproducible evidence artifacts (QEMU logs, validator output)
- baseline integrity checks for boot image payload

Out of scope:
- advanced production hardening internals (e.g., key provisioning, tamper response)
- full key lifecycle architecture
- authenticated image signing or encryption (baseline uses CRC32 checksums only)
- real hardware validation (QEMU-only baseline)

## Reporting a Vulnerability

For non-sensitive security issues:
- open a GitHub issue in this repository with prefix `[SECURITY]`
- include reproduction steps, expected behavior, observed behavior, and environment details

For potentially sensitive findings:
- do not post exploit details publicly
- open a minimal private contact request via GitHub issue (without exploit details) and request a secure follow-up channel

## Response Expectations

Target response times:
- acknowledgement: within 5 business days
- triage update: within 10 business days
- resolution plan (or scope decision): within 20 business days

These targets are best-effort for a solo-maintained repository and may vary with hardware availability.

## Support Window

Public baseline support is best-effort and scoped to:
- reproducibility issues in documented setup/validation paths
- correctness issues in published baseline behavior

This repository does not provide guaranteed SLA support. Paid engagements can define explicit response windows and acceptance criteria.
