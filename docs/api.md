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
  "accepted_panels": 115,
  "rejection_rate": 6.504065040650407,
  "net_production_time": 130.1,
  "downtime_rate": 13.554817275747509,
  "quality_status": "warning",
  "downtime_status": "warning",
  "sustainability_status": "below_target",
  "overall_status": "warning",
  "flags": [
    "high_rejection_rate",
    "downtime_above_target",
    "recycled_material_below_target"
  ],
  "main_issue": "high_rejection_rate"
}
```

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
