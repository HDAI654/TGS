# Contributing to TGS

Thank you for considering contributing to TGS! We welcome all contributions – from bug reports and feature requests to code improvements and documentation updates.

## How Can I Contribute?

### Reporting Bugs

- Before opening an issue, please search existing issues to avoid duplicates.
- Use the provided issue template and include:
  - A clear title and description.
  - Steps to reproduce the bug.
  - Expected and actual behavior.
  - Environment details (OS, Python version, Docker version).

### Suggesting Enhancements

- Open a feature request with a detailed description of the proposed change.
- Explain why this enhancement would be useful for the community.

### Code Contributions

1. **Fork the repository** and create your branch from `main`.
2. **Set up the development environment**:
   ```bash
   docker compose up --build
   ```
3. **Write tests** for your changes (unit, integration, or e2e as appropriate).
4. **Run the test suite** to ensure all tests pass:
   ```bash
   sh run_tests.sh
   ```
5. **Format your code** with `black`:
   ```bash
   black .
   ```
6. **Commit your changes** following [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: add channel search filter`).
7. **Push to your fork** and open a Pull Request against the `main` branch.

### Pull Request Guidelines

- Keep PRs focused on a single topic.
- Include a clear description of the changes and the problem they solve.
- Reference any related issues.
- Ensure all CI checks pass (formatting, tests, linting).

## Development Setup

### Using Docker (Recommended)

```bash
docker compose up --build
```

### Local Development (without Docker)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (copy from `docker-compose.yml`).
4. Run the app:
   ```bash
   uvicorn src.main:app --reload
   ```

## Style Guide

- **Python**: Follow PEP 8 and use `black` for formatting.
- **Type Hints**: Use type hints for all function signatures.
- **Docstrings**: Use Google-style docstrings for public APIs.
- **Commit Messages**: Follow Conventional Commits.

## Testing

- Write tests using `pytest`.
- Place unit tests in `test/unit/`, integration tests in `test/integration/`, and end‑to‑end tests in `test/e2e/`.
- Use `fakeredis` and in‑memory SQLite for fast, isolated tests.

## Need Help?

If you have any questions, feel free to open a discussion or reach out via the issue tracker.

**We look forward to your contributions! 🚀**
