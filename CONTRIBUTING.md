# Contributing to Binary Matrix Integration

Thank you for considering contributing to the Binary Matrix Integration! This document provides guidelines and steps for contributing.

## Code Style

- Follow Home Assistant's [Style Guidelines](https://developers.home-assistant.io/docs/development_guidelines)
- Use [Black](https://github.com/psf/black) for Python code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) guidelines

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

## Submitting Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b your-feature-name
   ```
2. Make your changes
3. Test your changes
4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```
5. Push to your fork:
   ```bash
   git push origin your-feature-name
   ```
6. Create a Pull Request from your fork to our main repository

## Pull Request Guidelines

- Describe your changes in detail
- Reference any related issues
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass
- Follow the existing code style

## Development Guidelines

1. **Version Control**
   - Make meaningful commit messages
   - Keep commits focused and atomic
   - Rebase your branch before submitting

2. **Code Quality**
   - Write clear, documented code
   - Add type hints to functions
   - Include docstrings for classes and methods
   - Add comments for complex logic

3. **Testing**
   - Write unit tests for new features
   - Update existing tests when modifying features
   - Ensure all tests pass before submitting

4. **Documentation**
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