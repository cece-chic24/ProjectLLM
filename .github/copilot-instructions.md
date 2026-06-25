# ProjectLLM Copilot Instructions

These instructions apply to the whole workspace.

## Hard rules
- `ui/` may only import from `app/controllers/`. It must never import directly from `transcription/`, `notes/`, `storage/`, `capture/`, `speakers/`, or `vision/`.
- All business logic belongs in controllers or services, not in UI files.
- Structured JSON is the source of truth. Text and Word exports must be generated from JSON, never the other way around.
- Never write real secrets into any file. `.env.example` must contain only placeholder values. Real secrets belong only in `.env`, which is gitignored.
- Every new module needs a focused unit test using fake or sample data. Do not depend on real network calls in tests.

## Build order
- Follow the phases in order.
- Do not start a phase until the previous phase is explicitly approved.
- Phase 0: repo bootstrap.
- Phase 1: manual transcription -> note -> export -> delete pipeline, with no recording yet.
- Phase 2: recording.

## Working style
- Prefer small, focused changes.
- Keep implementation logic out of UI files.
- Preserve the existing architecture and file boundaries.
- Add or update tests whenever behavior changes.
- Avoid real external dependencies in tests; use fakes or sample data instead.
