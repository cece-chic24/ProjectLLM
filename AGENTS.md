# ProjectLLM — Agent Instructions

This is a greenfield rebuild of a desktop app (Python, PySide6 UI) that
transcribes audio and generates AI notes from it.

## Hard rules — do not violate these
- ui/ may only import from app/controllers/. It must NEVER import
  directly from transcription/, notes/, storage/, capture/,
  speakers/, or vision/.
- All business logic lives in controllers/services, not in UI files.
- Structured JSON is the source of truth. Text/Word exports are generated
  FROM the JSON, never the other way around.
- Never write real secrets into any file. .env.example must only contain
  placeholder values. Real secrets only go in .env, which is gitignored.
- Every new module needs a focused unit test using fake/sample data —
  do not depend on real network calls (Azure OpenAI, etc.) in tests.

## Build order
Follow the phases in order. Do not start a phase until I explicitly say
the previous phase is approved. Phase 0 = repo bootstrap. Phase 1 = manual
transcription -> note -> export -> delete pipeline (no recording yet).
Phase 2 = recording.
