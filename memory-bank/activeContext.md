# Active Context

## Current Work Focus
The current focus is on establishing the **Memory Bank** to document the existing codebase and ensure context preservation for future development sessions. The project structure is already in place with Django apps, models, and Docker configuration.

## Recent Changes
- **Documentation**: Initialized Memory Bank files.
- **Infrastructure**: Project is containerized with Docker Compose (PostgreSQL + Django Web).
- **Backend**:
    - `ambiente` app established with `Ambiente` model.
    - `atividade` app established with `Atividade`, `Cliente`, `Endereco`, and `Referencia` models.

## Next Steps
- Verify current functionality by exploring views and templates (optional, but good for completeness).
- Identify any missing features or bugs based on the project brief.
- Continue development based on user requests.

## Active Decisions
- **Architecture**: Monolithic Django structure is being used.
- **Database**: PostgreSQL is the chosen database backend.
- **Deployment**: Docker Compose is used for local development/deployment.

