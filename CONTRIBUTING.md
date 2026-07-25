# Contributing Guidelines

Thank you for your interest in improving TextConvert!

## How to Contribute

1. Fork the repository and create your branch from `main`.
2. Make your changes in a focused, single-responsibility commit.
3. Ensure the code follows the existing style and passes the integration test:
   ```bash
   python tests/test_conversion.py
   ```
4. Update `README.md` if your change affects usage or architecture.
5. Open a pull request with a clear description of the change and motivation.

## Code Style

- Follow PEP 8 for Python code.
- Keep functions focused and add docstrings for public APIs.
- Avoid adding unrelated dependencies; prefer the standard library when possible.

## Reporting Issues

Please include:
- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Your operating system and Python version
