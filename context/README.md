# Context Files

**Always read these context files before coding.**

These documents keep the project grounded in its original goal, scope, and
constraints. They should be treated as the single source of truth for how the
project is intended to work.

## Working rules

- **Update `05_decisions.md` + `08_change_log.md` when you change anything**
  that affects behavior, architecture, or external interfaces.
- **Add new Cosine tasks to `07_cosine_task_log.md` with date + summary + files changed.**

If you are unsure whether a change is significant enough to document, err on the
side of documenting it.

## File overview

- `00_goal.md` – high-level business and technical goal.
- `01_scope.md` – what is in scope vs. explicitly out of scope.
- `02_dataset.md` – dataset details and download instructions.
- `03_architecture.md` – architecture and dataflow overview.
- `04_components.md` – components and their responsibilities.
- `05_decisions.md` – architectural and design decision records.
- `06_metrics_and_targets.md` – metrics and target ranges.
- `07_cosine_task_log.md` – log of Cosine tasks touching this repo.
- `08_change_log.md` – chronological changelog of repo changes.