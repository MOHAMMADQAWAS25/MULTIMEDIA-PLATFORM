# InkFig Backend

FastAPI starter backend for the InkFig digital art platform.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run

```powershell
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Test

```powershell
pytest
mypy src
```

## Structure

- `src/entities`: DTOs, enums, validation, domain exceptions
- `src/app`: use cases and business services
- `src/interface`: FastAPI routes and dependency providers
- `src/infrastructure`: repositories, database, external integrations
