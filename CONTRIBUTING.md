# Contributing to Audio Annotation Platform

Thank you for your interest in contributing to the Audio Annotation Platform! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title**: Descriptive summary of the issue
- **Steps to reproduce**: Detailed steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, component versions
- **Logs**: Relevant error messages or logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Use case**: Describe the problem you're trying to solve
- **Proposed solution**: Your suggested approach
- **Alternatives**: Other solutions you've considered
- **Additional context**: Screenshots, examples, etc.

### Code Contributions

We welcome code contributions! Areas where help is especially appreciated:

- **Performance improvements**: Optimize audio streaming, task assignment
- **Security enhancements**: Improve authentication, authorization
- **Documentation**: Improve guides, add examples
- **Testing**: Increase test coverage
- **New features**: Add functionality (discuss in an issue first)
- **Bug fixes**: Fix reported issues

## Development Setup

### Prerequisites

- Python 3.10+ (3.11 recommended)
- Docker and Docker Compose
- Redis server
- PostgreSQL 12+
- Git

### Local Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/audio-annotation-platform.git
   cd audio-annotation-platform
   ```

2. **Set up middleware development:**
   ```bash
   cd middleware
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start Label Studio:**
   ```bash
   cd label-studio
   ./setup.sh  # Configure environment
   docker network create label-studio-net
   docker compose up -d
   ```

4. **Configure middleware:**
   ```bash
   cd middleware
   cp config.env.example config.env
   # Edit config.env with your Label Studio API key
   ```

5. **Start middleware in development mode:**
   ```bash
   cd middleware
   source venv/bin/activate
   python app.py
   ```

### Running Tests

```bash
cd middleware
source venv/bin/activate

# Run basic health check
curl http://localhost:8010/api/health

# Test with frontend
# Open middleware/web/transcription_frontend_template.html in browser
```

## Coding Standards

### Python

- **Style**: Follow PEP 8
- **Type hints**: Use type annotations where possible
- **Docstrings**: Document functions, classes, and modules
- **Imports**: Group standard library, third-party, and local imports

Example:
```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def get_available_tasks(agent_id: Optional[int] = None) -> list[int]:
    """
    Get list of available task IDs, optionally filtering by agent.

    Args:
        agent_id: Optional agent ID to exclude their skipped tasks

    Returns:
        List of available task IDs
    """
    # Implementation
    pass
```

### File Organization

- Keep files focused on a single responsibility
- Use clear, descriptive names
- Group related functionality
- Avoid deep nesting

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors with context
- Don't expose sensitive information in errors

## Commit Guidelines

### Commit Messages

Follow the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(middleware): add task priority support

Implement priority queue for urgent tasks. High-priority tasks
are assigned first regardless of creation time.

Closes #123

---

fix(audio): resolve range request header parsing

Fixed bug where range requests with multiple ranges failed.
Now correctly handles single range requests.

Fixes #456

---

docs(api): add WebSocket endpoint documentation

Document real-time task update WebSocket API including
connection handling and message format.
```

### Commit Best Practices

- Keep commits atomic (one logical change per commit)
- Write clear, descriptive commit messages
- Reference relevant issues
- Don't commit sensitive data (API keys, passwords)
- Test before committing

## Pull Request Process

### Before Submitting

1. **Create an issue** (if one doesn't exist) describing the change
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Make your changes** following coding standards
4. **Test your changes** thoroughly
5. **Update documentation** if needed
6. **Commit your changes** with clear messages

### Submitting the PR

1. **Push your branch:**
   ```bash
   git push origin feat/your-feature-name
   ```

2. **Create pull request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Link to related issue(s)
   - Screenshots (if UI changes)
   - Testing instructions

3. **PR template:**
   ```markdown
   ## Description
   Brief description of changes

   ## Related Issue
   Closes #123

   ## Changes Made
   - Added X feature
   - Fixed Y bug
   - Updated Z documentation

   ## Testing
   - [ ] Tested locally
   - [ ] Manual testing steps: ...
   - [ ] All existing features still work

   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Documentation updated
   - [ ] No sensitive data committed
   - [ ] Commits are clean and well-organized
   ```

### Review Process

- Maintainers will review your PR
- Address feedback and make requested changes
- Once approved, maintainers will merge

### After Merge

- Delete your branch
- Pull latest changes from main
- Celebrate! 🎉

## Testing

### Manual Testing

1. **Start all services:**
   ```bash
   docker compose up -d  # Label Studio
   sudo systemctl start ls-middleware  # Middleware
   ```

2. **Test basic workflow:**
   - Import audio files
   - Request task via API
   - Stream audio file
   - Submit transcription
   - Verify in Label Studio

3. **Test edge cases:**
   - Skip task functionality
   - Cooldown behavior
   - Audio format support
   - Error handling

### Browser Testing

Use the provided frontend template:
```bash
# Update serverUrl in middleware/web/transcription_frontend_template.html
# Open in browser and test complete workflow
```

## Documentation

### What to Document

- **New features**: Add to README.md and API_REFERENCE.md
- **API changes**: Update API_REFERENCE.md
- **Architecture changes**: Update ARCHITECTURE.md
- **Configuration options**: Update relevant config documentation
- **Troubleshooting**: Add to README.md common issues section

### Documentation Style

- Use clear, simple language
- Include code examples
- Add diagrams for complex concepts
- Keep up-to-date with code changes

## Questions?

- **General questions**: Open a discussion on GitHub
- **Bug reports**: Create an issue
- **Feature requests**: Create an issue with enhancement label
- **Security issues**: Email directly to maintainers (see README.md)

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.

---

Thank you for contributing to Audio Annotation Platform! 🎙️✨
