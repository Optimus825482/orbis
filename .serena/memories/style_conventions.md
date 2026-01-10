# Code Style and Conventions for ORBIS

## Naming Conventions
- **Variables & Functions:** `snake_case` (e.g., `calculate_house_cusps`)
- **Classes:** `PascalCase` (e.g., `AstroData`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_MODEL`)

## Code Organization
- **Business Logic:** Keep calculation logic in `astro_calculations.py` and interpretation logic in `ai_interpretations.py`.
- **Routes:** Define API and view endpoints in `routes.py`.
- **Configuration:** Use `env_config.py` for dynamic configuration and environment variables.

## Guidelines
- **Statelessness:** The backend should remain stateless to support serverless deployment. Use client-side `localStorage` for user data persistence.
- **Error Handling:** Use try-except blocks with logging. Avoid bare `except:`; catch specific exceptions where possible.
- **Documentation:** Use docstrings for complex functions. Explain the "why" behind astrological calculations.
