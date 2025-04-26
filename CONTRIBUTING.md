# Contributing to Binary Matrix Integration

Thank you for considering contributing to the Binary Matrix Integration! This document provides guidelines and steps for contributing.

## Commit Message Convention

This project uses semantic commit messages to automate version management. The commit message format is:

```
<type>: <description>

[optional body]

[optional footer]
```

### Types:
- `feat`: A new feature (bumps minor version)
- `fix`: A bug fix (bumps patch version)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Breaking Changes

To indicate a breaking change, include "BREAKING CHANGE:" in your commit message body:

```
feat: change output numbering scheme

BREAKING CHANGE: Output numbers now start from 0 instead of 1
```

This will trigger a major version bump.

## Version Management

The project uses automated semantic versioning:
- Major version (x.0.0): Breaking changes
- Minor version (0.x.0): New features
- Patch version (0.0.x): Bug fixes and small changes

Version numbers are automatically updated based on commit messages when pushing to main/master.

## Development Environment Setup

1. Fork the repository
2. Clone your fork
3. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Testing

1. Run tests before submitting:
   ```bash
   pytest
   ```
2. Ensure code passes style checks:
   ```bash
   black .
   flake8 .
   isort .
   ```

## Pull Request Process

1. Create a new branch for your changes:
   ```bash
   git checkout -b your-feature-name
   ```
2. Make your changes
3. Test your changes
4. Commit with semantic commit message
5. Push to your fork
6. Create a Pull Request

### Pull Request Guidelines

- Use semantic commit messages
- Describe your changes in detail
- Reference any related issues
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass

## Development Guidelines

1. **Code Quality**
   - Write clear, documented code
   - Add type hints to functions
   - Include docstrings for classes and methods
   - Add comments for complex logic

2. **Testing**
   - Write unit tests for new features
   - Update existing tests when modifying features
   - Ensure all tests pass before submitting

3. **Documentation**
   - Update README.md if needed
   - Document new features
   - Update configuration examples
   - Add inline documentation for complex code

## Need Help?

- Open an issue for questions
- Check existing issues and discussions
- Review the integration documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.