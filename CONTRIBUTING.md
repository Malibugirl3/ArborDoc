# Contributing to ArborDoc

Thank you for your interest in contributing to ArborDoc!

## Development setup

```bash
git clone https://github.com/Malibugirl3/ArborDoc.git
cd ArborDoc

# Poetry (recommended)
poetry install
poetry install --extras server   # optional: REST API tests

# Or pip
pip install -e ".[server]"
```

## Running tests

```bash
pytest
```

## Reporting issues

Please use [GitHub Issues](https://github.com/Malibugirl3/ArborDoc/issues) and choose the appropriate template:

- **Bug report** — include reproduction steps, expected vs. actual behavior, and your environment (OS, Python version).
- **Feature request** — describe the use case and proposed behavior.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Make your changes and add or update tests when applicable.
3. Ensure `pytest` passes locally.
4. Open a pull request with a clear description of what changed and why.
5. Link any related issue (e.g. `Fixes #123`).

### Developer Certificate of Origin (DCO)

By contributing, you agree that your contributions are your own work and you have the right to submit them under the project's MIT License.

Please sign off your commits:

```text
Signed-off-by: Your Name <your.email@example.com>
```

You can add this automatically with `git commit -s`.

## Code style

- Match the existing code style and naming conventions in the file you are editing.
- Keep changes focused; prefer small, reviewable pull requests.
