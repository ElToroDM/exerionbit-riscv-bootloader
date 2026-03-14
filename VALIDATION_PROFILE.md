# Validation Profile — RISC-V QEMU Bootloader

Purpose: define canonical validation defaults and PASS/FAIL criteria for this repository.

## 1. Defaults (locked)

- QEMU-based protocol validation as default execution path
- Default full validation timeout: 10 seconds
- Expected output parser evaluates deterministic token flow
- Missing visual media is non-blocking

## 2. Canonical token families

- Bootloader tokens: `BL_EVT:<TOKEN>[:VALUE]`
- Application tokens: `APP_EVT:<TOKEN>[:VALUE]`
- Transitional human-readable protocol messages may coexist as compatibility output

## 3. Minimum pass criteria

### T1 Normal handoff
Required:

1. `BL_EVT:DECISION_NORMAL`
2. `BL_EVT:APP_CRC_CHECK`
3. `BL_EVT:APP_CRC_OK`
4. `BL_EVT:LOAD_APP`
5. `BL_EVT:HANDOFF`
6. `BL_EVT:HANDOFF_APP`
7. `APP_EVT:START`
8. `APP_EVT:BOOTLOADER_HANDOFF_OK`

### T2 Recovery path
Required:

- `BL_EVT:DECISION_RECOVERY`
- no application handoff while invalid image condition persists

### T3 Update protocol baseline
Required:

1. `BL_EVT:DECISION_UPDATE`
2. `BL_EVT:READY_FOR_UPDATE`
3. `BL_EVT:READY_FOR_CHUNK`
4. `BL_EVT:CHUNK_OK:0`
5. `BL_EVT:UPDATE_SESSION_END`
6. `BL_EVT:APP_CRC_OK`

### T4 Update integrity pass
Required:

- `BL_EVT:APP_CRC_CHECK`
- `BL_EVT:APP_CRC_OK`

### T5 Update integrity fail
Required:

- `BL_EVT:APP_CRC_FAIL`
- no handoff to invalid payload

## 4. Evidence artifacts per release

Required:

- `docs/evidence/<release>/expected-vs-observed.md`
- `docs/evidence/<release>/logs/*.log`

Optional:

- terminal capture media under `docs/media/<release>/`
