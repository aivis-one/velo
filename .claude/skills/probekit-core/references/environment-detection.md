# ProbeKit Environment Detection — Core Reference

Standard procedure for detecting project environment. All ProbeKit skills use this.

## Step 1 — Read ENVIRONMENT.md

Check for `ENVIRONMENT.md` in the project (common locations: root, `docs/`, `docs/01_reference/`).
If found — read it for shell type, tool pitfalls, project paths, known issues.
Never hardcode shell syntax — adapt to the detected environment.

## Step 2 — Detect Shell

| Signal | Shell |
|--------|-------|
| `$env:`, `Get-`, `.ps1` in history | PowerShell |
| `/bin/bash`, `#!/bin/bash`, `.bashrc` | Bash |
| `/bin/zsh`, `.zshrc` | Zsh |
| `COMSPEC` contains `cmd.exe` | CMD (rare) |

Shell-specific rules:
- **PowerShell**: use single quotes for `-k` patterns in pytest; use `&` to call executables with spaces; use `/dev/null` equivalent `$null`; semicolons to chain commands
- **Bash/Zsh**: standard Unix invocation; use `&&` to chain; redirect to `/dev/null`
- Always quote paths with spaces using double quotes

## Step 3 — Detect Language and Framework

Scan project root for markers in this priority order:

### Python
| Marker | Framework |
|--------|-----------|
| `pyproject.toml` with `[tool.pytest]` | pytest |
| `pytest.ini`, `setup.cfg [tool:pytest]` | pytest |
| `requirements.txt`, `Pipfile`, `poetry.lock` | Python project |
| `from fastapi` in source | FastAPI |
| `from flask` in source | Flask |
| `from django` in source | Django |
| `import sqlalchemy` in source | SQLAlchemy |

### JavaScript / TypeScript
| Marker | Framework |
|--------|-----------|
| `package.json` with `"jest"` | Jest |
| `package.json` with `"vitest"` | Vitest |
| `package.json` with `"mocha"` | Mocha |
| `next.config.*` | Next.js |
| `express` in dependencies | Express |
| `.ts` files + `tsconfig.json` | TypeScript |

### Go
| Marker | Framework |
|--------|-----------|
| `go.mod` | Go project |
| `*_test.go` files | Go testing (stdlib) |
| `testify` in `go.mod` | Testify |

### GDScript / Godot
| Marker | Framework |
|--------|-----------|
| `project.godot` | Godot project |
| `addons/gut/` directory | GUT test framework |
| `.gutconfig.json` | GUT configured |
| `.gd` file extensions | GDScript |

### Java
| Marker | Framework |
|--------|-----------|
| `pom.xml` | Maven |
| `build.gradle` | Gradle |
| JUnit imports in test files | JUnit |

### Rust
| Marker | Framework |
|--------|-----------|
| `Cargo.toml` | Cargo |
| `#[test]` in source | Rust test |

## Step 4 — Detect Test Structure

Look for existing test directories and conventions:
- `tests/`, `test/`, `__tests__/`, `spec/`, `specs/`
- `*_test.go`, `test_*.py`, `*.test.ts`, `*.spec.ts`
- `conftest.py`, `jest.config.*`, `vitest.config.*`
- `res://test/` (Godot)

If existing tests found → match their conventions (naming, location, fixtures).
If no tests found → use language-standard defaults.

## Step 5 — Detect Package Manager

| Marker | Manager |
|--------|---------|
| `package-lock.json` | npm |
| `yarn.lock` | Yarn |
| `pnpm-lock.yaml` | pnpm |
| `poetry.lock` | Poetry |
| `Pipfile.lock` | Pipenv |
| `requirements.txt` (alone) | pip |
| `go.sum` | Go modules |
| `Cargo.lock` | Cargo |

## Usage in Skills

Each skill should run environment detection in Step 1 and record:
- `language`: primary language
- `framework`: web/test framework
- `shell`: shell type for command execution
- `test_framework`: test runner
- `package_manager`: dependency manager
- `existing_tests`: boolean + location

Pass these to all subsequent steps. Never assume — always detect.
