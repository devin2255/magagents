# Contributing to TRUMPTOPIA AI

Thank you for your interest in contributing to TRUMPTOPIA AI! Together we can Make AI Agents Great Again! 🇺🇸

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Testing](#testing)
- [Documentation](#documentation)

---

## Code of Conduct

This project is a **satire/parody** project for educational purposes. When contributing:

- Keep it light-hearted and educational
- Focus on the technical aspects of multi-agent systems
- Respect all contributors regardless of political views
- No actual political advocacy

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Docker (optional but recommended)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork:
git clone https://github.com/YOUR_USERNAME/trumptopia-ai.git
cd trumptopia-ai

# Add upstream remote
git remote add upstream https://github.com/devin2255/trumptopia-ai.git
```

---

## Development Setup

### Option 1: Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Access dashboard
open http://localhost:7892

# View logs
docker-compose logs -f
```

### Option 2: Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 tests/test_trumptopia.py

# Start development server
bash scripts/run_loop.sh
```

---

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Relevant logs or error messages

Example:
```markdown
**Bug:** Dashboard not loading tasks

**Steps to reproduce:**
1. Start server with `python3 dashboard/server.py`
2. Open http://localhost:7892
3. Click on "Task Board" tab

**Expected:** Tasks should display
**Actual:** Empty board shown

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.11
- Browser: Chrome 120
```

### Suggesting Features

Feature requests are welcome! Please:

- Check if the feature already exists
- Describe the use case
- Explain how it fits the "government" metaphor
- Consider if it's educational/demonstrative

### Pull Requests

1. **Create a branch**
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   python3 tests/test_trumptopia.py
   ```

4. **Commit with clear message**
   ```bash
   git commit -m "Add feature: C-SPAN live debate panel"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/my-new-feature
   ```
   Then open a Pull Request on GitHub.

---

## Style Guidelines

### Python Code Style

Follow PEP 8 with these specifics:

```python
# Good
class TrumptopiaOrchestrator:
    """Central orchestrator for the system."""
    
    def create_task(self, title: str, description: str = "") -> Task:
        """Create a new task.
        
        Args:
            title: Task title
            description: Task description
            
        Returns:
            Created Task object
        """
        # Implementation
        pass

# Bad
class trumptopiaorchestrator:
    def createTask(self,title,desc=""):
        # missing docstring, unclear naming
        pass
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `TaskScheduler`)
- **Functions/Variables**: `snake_case` (e.g., `fire_agent`)
- **Constants**: `UPPER_CASE` (e.g., `MAX_RETRY`)
- **Private**: `_leading_underscore` (e.g., `_scheduler`)

### Trump-Style Messages

When adding Trump-style messages:

```python
# Good - enthusiastic, simple vocabulary
"TREMENDOUS success! Nobody does it better!"

# Bad - too complex
"The task has been completed with remarkable efficiency"

# Good - uses catchphrases
"You're FIRED!!! Total disaster!!!"

# Good - hashtags
"#MAGA #Winning #BestAgents"
```

---

## Commit Messages

Use clear, descriptive commit messages:

```
Type: Brief description (50 chars or less)

More detailed explanation if needed.

- Bullet points for multiple changes
- Reference issues: Fixes #123
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style (formatting, missing semi colons, etc)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Examples:
```bash
feat: Add C-SPAN live debate panel to dashboard

- Real-time agent debate visualization
- Vote tracking for bills
- Senator stance indicators

Fixes #42
```

```bash
fix: Correct efficiency calculation in DOGE auditor

Was dividing by wrong denominator, causing inflated scores.
```

```bash
docs: Add API examples for tariff negotiation

Includes Python code samples and expected outputs.
```

---

## Testing

### Running Tests

```bash
# Run all tests
python3 tests/test_trumptopia.py

# Run specific test class
python3 tests/test_trumptopia.py TestTrumpStyleFormatter

# Run with verbose output
python3 tests/test_trumptopia.py -v
```

### Writing Tests

Add tests for new features:

```python
def test_new_feature(self):
    """Test description of what this tests."""
    # Setup
    orch = TrumptopiaOrchestrator()
    
    # Action
    result = orch.new_feature("test")
    
    # Assert
    self.assertTrue(result.success)
    self.assertEqual(result.value, expected)
```

### Test Coverage

Aim for:
- 80%+ coverage for new code
- 100% coverage for critical paths (orchestrator, scheduler)
- Test edge cases and error conditions

---

## Documentation

### Code Documentation

All public functions should have docstrings:

```python
def calculate_tariff(self, agent_id: str, base_amount: float) -> Tuple[float, float, str]:
    """Calculate tariff for resource trading.
    
    Args:
        agent_id: Agent requesting resources
        base_amount: Base amount of resources
        
    Returns:
        Tuple of (tariff_rate, total_amount, tariff_type)
        
    Example:
        >>> rate, total, type = calc_tariff("treasury", 1000.0)
        >>> print(f"Rate: {rate*100}%, Total: {total}")
        Rate: 10.0%, Total: 1100.0
    """
```

### Documentation Files

Update relevant docs when adding features:

- `README.md` - User-facing overview
- `docs/ARCHITECTURE.md` - Technical architecture
- `docs/API.yaml` - API specification
- `examples/EXAMPLES.md` - Usage examples

---

## Areas for Contribution

### High Priority

1. **Frontend Improvements**
   - Real-time WebSocket updates
   - Mobile-responsive design
   - Dark mode theme

2. **Testing**
   - Integration tests
   - Frontend tests (Jest/Cypress)
   - Performance benchmarks

3. **Documentation**
   - Video tutorials
   - Interactive examples
   - Deployment guides

### Medium Priority

1. **New Features**
   - C-SPAN debate visualization
   - Election system for agent rotation
   - Lobbying mechanism

2. **Integrations**
   - Slack connector
   - Discord bot
   - Webhook notifications

3. **DevOps**
   - Kubernetes deployment
   - Monitoring/alerting
   - CI/CD improvements

### Fun/Satirical

1. **New Agent Types**
   - Press Secretary (media relations)
   - Chief of Staff (coordination)
   - Special Prosecutor (investigations)

2. **Events**
   - State of the Union address
   - Campaign rallies
   - Debate nights

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Awarded "Cabinet Positions" (fun titles)

Top contributors may receive:
- 🏆 "Secretary of the Treasury" (most code)
- 🎖️ "Medal of Freedom" (best bug fixes)
- 📜 "Presidential Citation" (best documentation)

---

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Check existing documentation first

---

**Make AI Agents Great Again! 🇺🇸**

Thank you for contributing!
