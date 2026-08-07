# Contributing to AIdle Openworld

Thank you for your interest in contributing to AIdle Openworld. This file explains how to set up a development environment, coding standards, and the contribution workflow.

1. Getting started

- Fork the repository and create a branch from `main` for your work. Name branches descriptively: `feat/<short-desc>`, `fix/<short-desc>`, `doc/<short-desc>`.
- Run the Godot project by opening the `game/` folder in Godot 4.3.
- Install Python dependencies (if present):
  ```bash
  python -m pip install -r orchestration/requirements.txt
  ```

2. Development workflow

- Development stages: `READY -> CLAIMED -> IN_PROGRESS -> REVIEW_REQUESTED -> VERIFIED -> ACCEPTED`.
- One writer per file. If you plan to edit a file, claim it in your write lease (add a note in your PR or issue referencing your intent).
- Open a Pull Request from your feature branch into `main`. Reference any work order or issue numbers.

3. Coding conventions

- Godot/GDScript
  - Use Godot 4.3-compatible APIs.
  - Follow the official style: snake_case for methods and variables, PascalCase for classes.
  - Scenes should avoid embedding provider credentials or secrets.

- Python
  - Follow PEP8. Use black/isort where practical.
  - Type hints are encouraged for public functions.

- Documentation
  - Keep docs in `AIdle_Openworld_Blueprint_v1.1/` and `orchestration/` where applicable.
  - Update the blueprint SSOT when designs change. Follow the Vision Lock and Architecture Lock before making design or runtime changes.

4. Testing and QA

- Provide headed QA evidence for art/visual changes derived from the mockup SSOT (see `orchestration/control/mockup_ssot_v2/` and the 100% mockup fidelity requirement in `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md`).
- For gameplay changes, include steps to reproduce, test scenes, and a short checklist of acceptance criteria in the PR description.

5. Pull request checklist

- [ ] Branched from `main` and up to date
- [ ] Descriptive PR title and summary
- [ ] Reference to the relevant work order or issue
- [ ] Tests or reproduction steps included (if applicable)
- [ ] No credentials or secrets in the diff
- [ ] One writer per file is respected

6. Review and acceptance

- PRs follow the acceptance ladder. Red/Blue/Purple roles apply: Red finds, Blue patches once approved, Purple verifies and never patches.
- If a change affects visual assets sourced from `MOCKUP_SSOT_V2`, include headed screenshot comparisons and QA evidence. The 100% mockup fidelity law applies.

7. Code of Conduct

- All contributors must follow the CODE_OF_CONDUCT.md.

8. Questions

- If you're unsure about scope, read `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md` and `orchestration/ARCHITECTURE_LOCK.md` before implementing. If still unsure, open an issue with the `clarification` label or ping the project owner.

