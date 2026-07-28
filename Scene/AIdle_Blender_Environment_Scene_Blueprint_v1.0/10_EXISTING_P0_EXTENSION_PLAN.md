# Existing P0 Bridge Extension Plan

Mở rộng repo thật `E:/AIdle_Blender_Bridge_P0` theo hướng không phá Character API.

```text
app/
├── api/
│   ├── jobs.py                 # current character endpoint
│   └── environment_jobs.py
├── models.py                   # current strict character models
├── environment_models.py       # new strict environment models
├── services/
│   ├── blender_runner.py
│   ├── job_service.py          # current character service
│   └── environment_job_service.py
blender_scripts/
├── worker_entry.py             # current character worker
└── environment_worker_entry.py
config/
├── environment_templates.yaml
├── environment_modules.yaml
├── environment_world_profiles.yaml
└── environment_operation_allowlist.yaml
storage/generated_quarantine/
```

## Không dùng chung worker entry

Character và environment chia entrypoint để giảm blast radius.

## Dùng chung

- settings
- path policy
- idempotency
- job receipt
- log capture
- timeout
- quarantine
- hash manifest
- health endpoint
- một Bridge-wide single-worker lease (`max_active_jobs = 1`)

## P0E API additions

```text
GET /v1/environment/templates
GET /v1/environment/modules
POST /v1/environment/jobs
GET /v1/environment/jobs/{job_id}
POST /v1/environment/jobs/{job_id}/cancel
```

## P0E tests

1. reject unknown world profile
2. reject unknown module
3. reject arbitrary operation
4. reject absolute path
5. duplicate request returns same logical job or conflict according policy
6. deterministic mock manifest
7. cancel queued job
8. real probe exports GLB and preview
9. artifact paths remain quarantine-relative
10. character API regression remains green
11. changed payload with same idempotency key fails closed
12. client cannot raise resource budget or choose output path
13. server-mediated receipt reaches `QUARANTINED_COMPLETE`
14. external path, embedded script and URL fields are impossible in schema
