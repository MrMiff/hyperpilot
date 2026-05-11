# 🤝 Contributing to HyperPilot

Thanks for your interest in contributing! HyperPilot is built for hackathons and demo projects — every contribution helps make it better.

## 🚀 Quick Start

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/hyperpilot.git
cd hyperpilot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install pytest ruff black

# 4. Create a branch
git checkout -b feature/amazing-feature

# 5. Make changes & test
streamlit run app.py  # Test locally
pytest tests/ -v      # Run tests

# 6. Commit & push
git commit -m "✨ Add amazing feature"
git push origin feature/amazing-feature

# 7. Open a Pull Request
```

## 📋 Development Guidelines

### Code Style
- **Formatter:** Black (default settings)
- **Linter:** Ruff
- Run before committing:
  ```bash
  black .
  ruff check . --fix
  ```

### Commit Messages
Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `style:` — Code style (formatting, etc.)
- `refactor:` — Code refactoring
- `test:` — Adding tests
- `chore:` — Maintenance tasks

Examples:
```
feat: add voice command support
fix: ADB connection timeout on wireless
docs: update installation guide
```

### Project Structure
```
hyperpilot/
├── app.py              # Streamlit UI
├── adb_controller.py   # ADB command layer
├── agent.py            # NLP command parser
├── tests/              # Test suite
├── assets/             # Images, diagrams
└── .github/workflows/  # CI/CD
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_agent.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🐛 Bug Reports

Found a bug? Please open an issue with:
- **Description:** What happened?
- **Steps to reproduce:** How to trigger it
- **Expected behavior:** What should happen
- **Environment:** OS, Python version, device model

## 💡 Feature Requests

Have an idea? Open an issue with:
- **Use case:** Why is this needed?
- **Proposed solution:** How it should work
- **Alternatives considered:** Other approaches

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

<div align="center">

**Every contribution matters. Let's build something amazing together! 🚀**

</div>
