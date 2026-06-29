# Contributing to FreateOJ

Thank you for your interest in contributing to FreateOJ! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/freatevietnam/freateoj/issues) first
2. If not found, [open a new issue](https://github.com/freatevietnam/freateoj/issues/new)
3. Include:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, browser, Python version)

### Suggesting Features

1. [Open an issue](https://github.com/freatevietnam/freateoj/issues/new) with the `feature_request` template
2. Describe the feature, its use case, and implementation ideas

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run linter: `flake8`
5. Commit with a clear message
6. Push and create a Pull Request

### Pull Request Guidelines

- PR description should clearly describe the problem and solution
- Reference related issues with `Fixes #123`
- Include screenshots for UI changes
- Ensure code passes `flake8` checks
- Update documentation if needed

## Development Setup

### Prerequisites

- Python 3.13+
- PostgreSQL
- Node.js 26+

### Local Development

```bash
# Clone the repo
git clone https://github.com/freatevietnam/freateoj.git
cd freateoj

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb freateoj
python manage.py migrate
python manage.py loaddata demo

# Run development server
python manage.py runserver
```

### Building CSS

```bash
# Install Node dependencies
npm install

# Build both themes
./make_style.sh
```

## Coding Standards

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use `flake8` for linting
- Write docstrings for public functions

### JavaScript

- Use `prettier` for formatting (in `websocket/`)
- Follow existing code patterns

### CSS/SCSS

- Use SCSS for styles
- Follow the existing design system in `resources/vars-common.scss`
- Build with `./make_style.sh` after changes

### Templates

- Use Jinja2 syntax
- Follow existing template patterns
- Support both light and dark themes

## Project Structure

```
freateoj/
├── dmoj/           # Django project settings
├── judge/          # Main app (models, views, forms)
├── templates/      # Jinja2 templates
├── resources/      # SCSS, JS, images
├── docs/           # Documentation
├── locale/         # Translations
├── websocket/      # Socket.IO event server
└── manage.py       # Django management
```

## Translation

Vietnamese translations are in `locale/vi/LC_MESSAGES`. Contributions welcome!

## Questions?

Join our [Discord](https://discord.gg/fC3kG3hQyn) or open an issue.
