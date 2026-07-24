# API Reference

This document captures the current API behavior for the implemented reference-data endpoints.
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

Reference data currently includes production lines, resin types, and shifts. These records are used by
future production sheet and lab test workflows.

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
