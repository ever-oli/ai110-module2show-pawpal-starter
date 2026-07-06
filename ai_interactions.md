# AI Interactions Log

**Setup:** I worked mobile-only for this project, so instead of an AI assistant inside VS Code, I collaborated with Claude in the Claude app. Claude wrote and executed the code in its sandboxed environment and showed me real terminal output; I acted as the lead architect — making design decisions, reviewing the code, and committing every file to GitHub myself through the mobile web editor. Automated verification happens through GitHub Actions, which runs the pytest suite on every push.

## Agent Workflow

**Files modified/created by the AI (reviewed and committed by me):**
- `diagrams/uml_draft.mmd`, `diagrams/uml_final.mmd`
- `pawpal_system.py` (skeleton first, then full implementation)
- `main.py`
- `tests/test_pawpal.py`
- `app.py` (replaced starter placeholders with real logic wiring)
- `.github/workflows/tests.yml`
- `README.md`

**What I asked for:** a phased build matching the project instructions — UML + skeletons, then core classes with a CLI demo, then tests, then Streamlit integration, then documentation.

**Decisions I made as architect:**
- Conflict detection checks **exact time matches only** (simple and predictable) rather than overlapping durations
- Included three extensions: priority-based scheduling, JSON persistence, and formatted CLI output
- Approved the design where the Scheduler stores no tasks and always reads through Owner → Pets → Tasks, keeping one source of truth
- Data model choices: dataclasses for Task/Pet, "HH:MM" strings for times, ISO date strings for due dates

**What the AI completed:** all code above, executed and verified in its environment (demo script output + 9/9 tests passing) before handing files to me.

**Manual corrections / human oversight:**
- I verified each file before committing and controlled the commit history so it reflects the actual build phases
- The AI's sandbox had no internet, so pytest couldn't be installed there; it verified the tests with an equivalent runner and flagged this honestly. We added GitHub Actions so the real `python -m pytest` output comes from CI, not from the AI's environment
- The AI could not access my repo directly (no GitHub connector available), so every change went through my review before landing

## Prompt strategy notes

- Working in phases (design → implement → test → integrate → document) kept each interaction focused, mirroring the "separate chat sessions" advice in the project instructions
- Answering structured design questions up front (conflict strategy, extensions, demo data) meant the AI built to my spec instead of guessing
