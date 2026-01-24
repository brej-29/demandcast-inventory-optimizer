# Architectural & Design Decisions

Record significant decisions that affect how this project is structured or how
it behaves. When in doubt, add an entry.

Use the following template:

- **ID** – Short identifier (e.g., `DEC-0001`).
- **Date** – YYYY-MM-DD (UTC).
- **Decision** – Summary of the choice made.
- **Status** – `Proposed`, `Accepted`, `Deprecated`, or `Rejected`.
- **Rationale** – Why this decision was made and what alternatives were considered.

## Decisions

| ID        | Date       | Decision                                         | Status   | Rationale |
|-----------|------------|--------------------------------------------------|----------|-----------|
| DEC-0001  | 2026-01-24 | Use Streamlit as the main UI for DemandCast     | Accepted | Streamlit is free, easy to deploy, and well-suited for interactive dashboards. |
| DEC-0002  | 2026-01-24 | Use a `src/` layout for the Python package      | Accepted | Encourages explicit imports and clean separation between library and app code. |
| DEC-0003  | 2026-01-24 | Keep data and model artifacts out of git        | Accepted | Avoids bloating the repo and leaking potentially sensitive or large files. |
| DEC-0004  | 2026-01-24 | Prefer CLI + scripts over notebooks for plumbing| Accepted | Notebooks focus on EDA; scripts handle repeatable operations (downloads, checks). |

Add new decisions below this table as the project evolves.