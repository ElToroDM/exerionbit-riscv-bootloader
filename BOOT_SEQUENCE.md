# Boot Sequence Specification — RISC-V QEMU Bootloader

Purpose: define the implemented and auditable boot state behavior, serial token contract, and deterministic protocol flow.

## 1. Deterministic behavior model

- Startup path is fixed and explicit: assembly entry (`_start`) then C `main()`
- Boot decision is explicit on UART input (`u`/`U` enters update mode)
- Validation checks are deterministic and centralized (`magic`, `size bounds`, `CRC32`)
- No hidden fallback branches: every path emits explicit bootloader state tokens

## 2. Serial token contract (canonical)

Canonical machine-parsable format:

`BL_EVT:<TOKEN>[:VALUE]`

Application format:

`APP_EVT:<TOKEN>[:VALUE]`

Implemented bootloader tokens:

- `BL_EVT:INIT`
- `BL_EVT:HW_READY`
- `BL_EVT:DECISION_NORMAL`
- `BL_EVT:DECISION_UPDATE`
- `BL_EVT:DECISION_RECOVERY`
- `BL_EVT:READY_FOR_UPDATE`
- `BL_EVT:READY_FOR_CHUNK`
- `BL_EVT:CHUNK_OK:<offset>`
- `BL_EVT:UPDATE_SESSION_END`
- `BL_EVT:UPDATE_START_FAIL`
- `BL_EVT:UPDATE_SETUP_FAIL`
- `BL_EVT:APP_CRC_CHECK`
- `BL_EVT:APP_CRC_OK`
- `BL_EVT:APP_CRC_FAIL`
- `BL_EVT:LOAD_APP`
- `BL_EVT:HANDOFF`
- `BL_EVT:HANDOFF_APP`

Implemented application tokens:

- `APP_EVT:START`
- `APP_EVT:BOOTLOADER_HANDOFF_OK`

Compatibility note:

- Human-readable messages (`BOOT?`, `OK`, `READY`, `CRC?`, `REBOOT`, `ERR:*`) are compatibility output only.
- Validation tooling should use `BL_EVT:*` and `APP_EVT:*` as the canonical oracle.

## 3. Protocol baseline

### 3.1 Normal boot sequence

1. Emit `BL_EVT:INIT`
2. Emit `BL_EVT:HW_READY`
3. Emit `BOOT?` prompt (compatibility layer)
4. Emit `BL_EVT:DECISION_NORMAL`
5. Emit `BL_EVT:APP_CRC_CHECK`
6. If image valid: emit `BL_EVT:APP_CRC_OK` then `LOAD_APP` -> `HANDOFF` -> `HANDOFF_APP`
7. Application emits `APP_EVT:START` and `APP_EVT:BOOTLOADER_HANDOFF_OK`

### 3.2 Update sequence (UART)

1. Emit `BL_EVT:DECISION_UPDATE`
2. Emit `BL_EVT:READY_FOR_UPDATE`
3. Emit `BL_EVT:APP_CRC_CHECK` and compatibility `OK`
4. Host sends `SEND <size>\n`
5. Bootloader erases app region, emits `BL_EVT:READY_FOR_CHUNK`, then compatibility `READY`
6. Host sends exactly `<size>` payload bytes
7. Bootloader emits `BL_EVT:CHUNK_OK:0`
8. Header commit succeeds: emit `BL_EVT:UPDATE_SESSION_END`, `BL_EVT:APP_CRC_OK`, then compatibility `CRC?`, `OK`, `REBOOT`
9. Platform policy applies (`PLATFORM_DIRECT_BOOT_AFTER_UPDATE` direct handoff in QEMU baseline)

Failure behavior:

- Command/size parse failure: `BL_EVT:UPDATE_START_FAIL` + `BL_EVT:APP_CRC_FAIL`
- Erase/header commit failure: `BL_EVT:UPDATE_SETUP_FAIL` + `BL_EVT:APP_CRC_FAIL`

## 4. Recovery baseline

Recovery path is entered when app validation fails or update mode fails.

- `BL_EVT:DECISION_RECOVERY` is emitted before hold loop
- No `BL_EVT:HANDOFF_APP` while recovery condition persists
- UART update remains available with explicit operator action (`u`/`U`)

## 5. Visual signaling

Visual evidence is terminal/log based.

## 6. Evidence links

- Validation profile: `VALIDATION_PROFILE.md`
- Setup and execution: `SETUP.md`
- Release evidence: `docs/evidence/<release>/`
