# API Reference

This document captures the current API behavior for the implemented production endpoints.
Interactive documentation is available locally through FastAPI Swagger UI at:

```text
http://localhost:8000/docs
```

## Base Path

All versioned endpoints are mounted under:

```text
/api/v1
```

The production router is mounted under:

```text
/api/v1/production
```

The lab router is mounted under:

```text
/api/v1/lab
```

## Reference Data

Reference data currently includes production lines, resin types, and shifts. Production sheets must
reference existing records from these tables before they can be created.

### Production Lines

Production line names are normalized for storage:

```text
" Line 1 " -> "line 1"
```

Endpoints:

```text
POST /api/v1/production/lines
GET  /api/v1/production/lines
GET  /api/v1/production/lines/{line_id}
```

Create request:

```json
{
  "name": "Line 1"
}
```

Create response:

```json
{
  "id": 1,
  "name": "line 1"
}
```

List query parameters:

```text
name: optional exact normalized name filter
limit: default 20, minimum 1, maximum 100
offset: default 0, minimum 0
```

### Resin Types

Resin type names are stripped for storage but keep capitalization because they may be codes.
Duplicate and search comparisons are case-insensitive.

```text
" pMDI " -> stored as "pMDI"
"pmdi"  -> matches "pMDI" for lookup
```

Endpoints:

```text
POST /api/v1/production/resin-types
GET  /api/v1/production/resin-types
GET  /api/v1/production/resin-types/{resin_type_id}
```

Create request:

```json
{
  "name": "pMDI"
}
```

Create response:

```json
{
  "id": 1,
  "name": "pMDI"
}
```

List query parameters:

```text
name: optional exact case-insensitive name filter
limit: default 20, minimum 1, maximum 100
offset: default 0, minimum 0
```

### Shifts

Shift letters are stripped and uppercased. Operator names are stripped for storage and searched
case-insensitively.

```text
shift_letter: " a " -> "A"
press_operator: " Jane Smith " -> "Jane Smith"
```

Endpoints:

```text
POST /api/v1/production/shifts
GET  /api/v1/production/shifts
GET  /api/v1/production/shifts/{shift_id}
```

Create request:

```json
{
  "shift_letter": "A",
  "press_operator": "Jane Smith",
  "line_operator": "Luis Costa"
}
```

Create response:

```json
{
  "id": 1,
  "shift_letter": "A",
  "press_operator": "Jane Smith",
  "line_operator": "Luis Costa"
}
```

List query parameters:

```text
shift_letter: optional exact normalized letter filter
press_operator: optional exact case-insensitive operator filter
line_operator: optional exact case-insensitive operator filter
limit: default 20, minimum 1, maximum 100
offset: default 0, minimum 0
```

## Error Behavior

Common responses:

```text
201 Created: record created successfully
200 OK: record or list returned successfully
400 Bad Request: invalid domain value handled by service logic
404 Not Found: requested id does not exist
409 Conflict: duplicate unique reference value
422 Unprocessable Entity: request/query validation failed
```

### Production Sheets

Production sheets capture the manufacturing record for a panel production run. A production sheet
requires an existing production line, shift, and resin type.

Endpoints:

```text
POST /api/v1/production/production-sheets
GET  /api/v1/production/production-sheets
GET  /api/v1/production/production-sheets/{production_sheet_id}
GET  /api/v1/production/production-sheets/{production_sheet_id}/assessment
```

Create request:

```json
{
  "production_ref": 20260805,
  "production_date": "2026-08-05T10:00:00Z",
  "production_line_id": 1,
  "batch_id": 1,
  "shift_id": 1,
  "panel_type": "MDF",
  "panel_length": "4880.00",
  "panel_width": "1200.00",
  "panel_thickness": "18.00",
  "forming_line_speed": 10.5,
  "press_temperature": 180.0,
  "press_pressure": 150.0,
  "press_factor": 0.8,
  "resin_type_id": 1,
  "production_duration": 150.5,
  "total_downtime": 20.4,
  "resin_dosed": "12.00",
  "paraffin_dosed": "4.00",
  "urea_dosed": "0.50",
  "percentage_recycled_material": 12,
  "panels_produced": 123,
  "panels_rejected": 8
}
```

Create response:

```json
{
  "id": 1,
  "production_ref": 20260805,
  "production_date": "2026-08-05T10:00:00Z",
  "production_line_id": 1,
  "batch_id": 1,
  "shift_id": 1,
  "panel_type": "MDF",
  "panel_length": "4880.00",
  "panel_width": "1200.00",
  "panel_thickness": "18.00",
  "forming_line_speed": 10.5,
  "press_temperature": 180.0,
  "press_pressure": 150.0,
  "press_factor": 0.8,
  "resin_type_id": 1,
  "production_duration": 150.5,
  "total_downtime": 20.4,
  "resin_dosed": "12.00",
  "paraffin_dosed": "4.00",
  "urea_dosed": "0.50",
  "percentage_recycled_material": 12.0,
  "panels_produced": 123,
  "panels_rejected": 8,
  "rejection_rate": 6.504065040650407,
  "created_at": "2026-08-05T00:07:39.528467Z",
  "updated_at": "2026-08-05T00:07:39.528467Z"
}
```

List query parameters:

```text
production_line_id: optional positive integer filter
shift_id: optional positive integer filter
resin_type_id: optional positive integer filter
production_ref: optional positive integer filter
batch_id: optional positive integer filter
panel_type: optional panel type filter, for example MDF
production_date_from: optional inclusive datetime lower bound
production_date_to: optional inclusive datetime upper bound
limit: default 20, minimum 1, maximum 100
offset: default 0, minimum 0
```

Results are ordered by `production_date` descending, with `id` descending as a tiebreaker so pagination is deterministic.

Example list request:

```text
GET /api/v1/production/production-sheets?production_line_id=1&panel_type=MDF&limit=20&offset=0
```

List response:

```json
[
  {
    "id": 1,
    "production_ref": 20260805,
    "production_date": "2026-08-05T10:00:00Z",
    "production_line_id": 1,
    "batch_id": 1,
    "shift_id": 1,
    "panel_type": "MDF",
    "panel_length": "4880.00",
    "panel_width": "1200.00",
    "panel_thickness": "18.00",
    "forming_line_speed": 10.5,
    "press_temperature": 180.0,
    "press_pressure": 150.0,
    "press_factor": 0.8,
    "resin_type_id": 1,
    "production_duration": 150.5,
    "total_downtime": 20.4,
    "resin_dosed": "12.00",
    "paraffin_dosed": "4.00",
    "urea_dosed": "0.50",
    "percentage_recycled_material": 12.0,
    "panels_produced": 123,
    "panels_rejected": 8,
    "rejection_rate": 6.504065040650407,
    "created_at": "2026-08-05T00:07:39.528467Z",
    "updated_at": "2026-08-05T00:07:39.528467Z"
  }
]
```

Example detail request:

```text
GET /api/v1/production/production-sheets/1
```

Detail response:

```json
{
  "id": 1,
  "production_ref": 20260805,
  "production_date": "2026-08-05T10:00:00Z",
  "production_line_id": 1,
  "batch_id": 1,
  "shift_id": 1,
  "panel_type": "MDF",
  "panel_length": "4880.00",
  "panel_width": "1200.00",
  "panel_thickness": "18.00",
  "forming_line_speed": 10.5,
  "press_temperature": 180.0,
  "press_pressure": 150.0,
  "press_factor": 0.8,
  "resin_type_id": 1,
  "production_duration": 150.5,
  "total_downtime": 20.4,
  "resin_dosed": "12.00",
  "paraffin_dosed": "4.00",
  "urea_dosed": "0.50",
  "percentage_recycled_material": 12.0,
  "panels_produced": 123,
  "panels_rejected": 8,
  "rejection_rate": 6.504065040650407,
  "created_at": "2026-08-05T00:07:39.528467Z",
  "updated_at": "2026-08-05T00:07:39.528467Z"
}
```

Example operational assessment request:

```text
GET /api/v1/production/production-sheets/1/assessment
```

Operational assessment response:

```json
{
  "production_sheet_id": 1,
  "production_ref": 20260805,
  "production_metrics": {
    "accepted_panels": 115,
    "net_production_time": 130.1
  },
  "quality": {
    "rejection_rate": 6.504065040650407,
    "status": "warning"
  },
  "downtime": {
    "downtime_rate": 13.554817275747509,
    "status": "warning"
  },
  "sustainability": {
    "recycled_material_percentage": 12.0,
    "status": "below_target"
  },
  "process_parameters": {
    "forming_line_speed": {
      "value": 10.5,
      "status": "within_target"
    },
    "press_factor": {
      "value": 0.8,
      "status": "within_target"
    },
    "press_pressure": {
      "value": 150.0,
      "status": "within_target"
    },
    "press_temperature": {
      "value": 180.0,
      "status": "within_target"
    }
  },
  "material_efficiency": {
    "chemical_total_dosed": "16.50",
    "resin_per_accepted_panel": "0.10",
    "paraffin_per_accepted_panel": "0.03",
    "urea_per_accepted_panel": "0.00",
    "chemical_dose_per_accepted_panel": "0.14"
  },
  "overall_status": "warning",
  "flags": [
    "high_rejection_rate",
    "downtime_above_target",
    "recycled_material_below_target"
  ],
  "main_issue": "high_rejection_rate"
}
```

Material efficiency metrics report chemical consumption per **accepted** panel — rejected panels
raise the chemical cost of each sellable unit. Values are rounded to two decimal places. When a
run has no accepted panels, the per-panel metrics are reported as `"0.00"` while the total still
reflects the chemicals actually used.

Process parameters are classified against target windows as
`within_target`, `below_target`, or `above_target`. Window boundaries are inclusive: a value
exactly at `target - tolerance` or `target + tolerance` counts as `within_target`. The current
targets are illustrative defaults for a single product family; in real manufacturing, press
windows are product-specific (panel type, thickness band), and per-product target configuration
is a planned future step.

Assessment thresholds (rejection rate warning/critical, downtime rate warning/critical, recycled
material target) are named service-level constants representing the current default policy.
In real manufacturing these targets are product-specific; per-product target configuration is a
planned future step.

Validation notes:

```text
production_line_id: must reference an existing production line
shift_id: must reference an existing shift
resin_type_id: must reference an existing resin type
production_ref: must be unique
panels_rejected: cannot be greater than panels_produced
total_downtime: cannot be greater than production_duration
percentage_recycled_material: must be between 0 and 100
```

Common production sheet errors:

```text
404 Not Found: referenced production line, shift, resin type, or production sheet id does not exist
409 Conflict: production_ref already exists
422 Unprocessable Entity: request, query, or path validation failed
```

### Lab Tests

Lab tests capture quality measurements for a produced panel: density, moisture, internal bond,
bending strength, elastic modulus, thickness swelling, water absorption, and formaldehyde
metrics. A lab test requires an existing production line and shift, and it must reference an
existing production sheet via `production_ref` — the sheet's `id` is stored as
`production_sheet_id`.

`calculated_density` and `elastic_modulus` are stored and validated as whole numbers (no decimal
places); all other measurement fields carry two decimal places.

Endpoints:

```text
POST /api/v1/lab/lab-tests
GET  /api/v1/lab/lab-tests
GET  /api/v1/lab/lab-tests/{lab_test_id}
```

Create request:

```json
{
  "lab_ref": 500123,
  "lab_test_date": "2026-08-05T14:00:00Z",
  "production_line_id": 1,
  "production_ref": 20260805,
  "batch_id": 1,
  "shift_id": 1,
  "panel_type": "MDF",
  "panel_thickness": "18.00",
  "actual_thickness": "18.20",
  "calculated_density": "650",
  "moisture_content": "8.00",
  "internal_bond": "0.50",
  "bending_strength": "20.00",
  "elastic_modulus": "2500",
  "thickness_swelling": "10.00",
  "water_absorption": "20.00",
  "formaldehyde_emission": "0.10",
  "formaldehyde_content": "5.00"
}
```

Create response:

```json
{
  "id": 1,
  "lab_ref": 500123,
  "lab_test_date": "2026-08-05T14:00:00Z",
  "production_line_id": 1,
  "production_sheet_id": 1,
  "batch_id": 1,
  "shift_id": 1,
  "panel_type": "MDF",
  "panel_thickness": "18.00",
  "actual_thickness": "18.20",
  "calculated_density": "650",
  "moisture_content": "8.00",
  "internal_bond": "0.50",
  "bending_strength": "20.00",
  "elastic_modulus": "2500",
  "thickness_swelling": "10.00",
  "water_absorption": "20.00",
  "formaldehyde_emission": "0.10",
  "formaldehyde_content": "5.00",
  "created_at": "2026-08-05T14:03:11.201933Z",
  "updated_at": "2026-08-05T14:03:11.201933Z"
}
```

List query parameters:

```text
production_line_id: optional positive integer filter
shift_id: optional positive integer filter
batch_id: optional positive integer filter
panel_type: optional panel type filter, for example MDF
panel_thickness: optional exact thickness filter
lab_test_date_from: optional inclusive datetime lower bound
lab_test_date_to: optional inclusive datetime upper bound
limit: default 20, minimum 1, maximum 100
offset: default 0, minimum 0
```

Results are ordered by `lab_test_date` descending, with `id` descending as a tiebreaker, matching
the production sheet listing's deterministic ordering.

Example list request:

```text
GET /api/v1/lab/lab-tests?panel_type=MDF&limit=20&offset=0
```

Example detail request:

```text
GET /api/v1/lab/lab-tests/1
```

Validation notes:

```text
production_line_id: must reference an existing production line
shift_id: must reference an existing shift
production_ref: must reference an existing production sheet
lab_ref: must be unique
calculated_density, elastic_modulus: whole numbers only, no decimal places
```

Common lab test errors:

```text
404 Not Found: referenced production line, shift, production reference, or lab test id does not exist
409 Conflict: lab_ref already exists
422 Unprocessable Entity: request, query, or path validation failed
```
