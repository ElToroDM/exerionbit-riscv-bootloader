# Expected vs Observed — v0.1

Scope: protocol baseline validation for the QEMU reference bootloader.

Observed artifacts:

- `docs/evidence/v0.1/logs/qemu_update_protocol.log`
- `docs/evidence/v0.1/logs/qemu_recovery_protocol.log`
- `docs/evidence/v0.1/logs/qemu_update_fail_protocol.log`

## Run context

- Date/time (UTC): 2026-03-14 13:05:31 UTC
- Commit: `25b1992`
- Python: `Python 3.12.9`
- QEMU: `QEMU emulator version 10.2.0 (v10.2.0-12105-g0f12d445bd)`
- Target: `qemu-system-riscv32 -M virt`

## Reproducible commands

1. Build baseline:

```bash
make all
make test-app
```

2. Capture normal/update-pass log:

```bash
python3 test_validator.py --uart-mirror-file docs/evidence/v0.1/logs/qemu_update_protocol.log
```

3. Capture recovery and update-fail logs:

- Recovery path log: run QEMU, press Enter at `BOOT?`, capture until `BL_EVT:DECISION_RECOVERY`.
- Update-fail log: run QEMU, send `u`, then send malformed command `BAD\n`, capture until `BL_EVT:UPDATE_START_FAIL` and `BL_EVT:APP_CRC_FAIL`.

## Checklist

- Normal handoff: expected `BL_EVT:HANDOFF_APP` + `APP_EVT:START` — observed: PASS (`qemu_update_protocol.log` contains `BL_EVT:HANDOFF_APP`, `APP_EVT:START`, `APP_EVT:BOOTLOADER_HANDOFF_OK`)
- Recovery behavior: expected no handoff on invalid image — observed: PASS (`qemu_recovery_protocol.log` shows `BL_EVT:DECISION_NORMAL` -> `BL_EVT:APP_CRC_CHECK` -> `BL_EVT:APP_CRC_FAIL` -> `BL_EVT:DECISION_RECOVERY`, with no `BL_EVT:HANDOFF_APP`)
- Update pass path: expected `BL_EVT:APP_CRC_OK` — observed: PASS (`qemu_update_protocol.log` shows `BL_EVT:DECISION_UPDATE`, `BL_EVT:READY_FOR_UPDATE`, `BL_EVT:READY_FOR_CHUNK`, `BL_EVT:CHUNK_OK:0`, `BL_EVT:UPDATE_SESSION_END`, `BL_EVT:APP_CRC_OK`)
- Update fail path: expected `BL_EVT:APP_CRC_FAIL` and safe path — observed: PASS (`qemu_update_fail_protocol.log` shows `ERR: CMD`, `BL_EVT:UPDATE_START_FAIL`, `BL_EVT:APP_CRC_FAIL`, and no handoff token)

Summary: PASS.

## Public claim mapping

- Claim: deterministic UART update baseline with CRC validation (`README.md`) -> Evidence: `qemu_update_protocol.log` + `qemu_update_fail_protocol.log`
- Claim: reproducible protocol behavior in QEMU (`README.md`) -> Evidence: reproducible commands above + all three `logs/*.log` artifacts
- Claim: recovery path blocks app handoff on invalid image (`BOOT_SEQUENCE.md`, `VALIDATION_PROFILE.md`) -> Evidence: `qemu_recovery_protocol.log`

Notes:

- Keep expected and observed results explicit.
- Attach command/procedure used for reproduction and date/version context.
