# 🧪 Python TDD & BDD Automation Suite

This repository contains a complete automation test suite developed using Test-Driven Development (TDD) and Behavior-Driven Development (BDD) principles. It's built for hands-on learning, quality assurance, and showcasing best practices in scalable Python test automation.

---

## 📦 Tech Stack

- **Language**: Python 3
- **Frameworks**:
  - `unittest` for TDD
  - `Behave` for BDD (Gherkin syntax)
- **CI/CD**: GitHub Actions
- **Linting**: Flake8
- **Test Coverage**: ~95%
- **Containerization**: Docker
- **Other Tools**: `Makefile`, `dotenv`, `.env` config handling

---

## 🚀 Features

- 📁 Clear modular structure with separation of concerns (`features/`, `service/`, `tests/`)
- ✅ 95%+ unit test coverage (demonstrates clean code practices)
- 🧪 Gherkin-style feature files for BDD scenarios
- 🐳 Dockerized setup for easy local development & portability
- 🛠️ GitHub Actions integrated for CI automation

---

## 🧰 Getting Started

### 📥 Clone the repository

```bash
git clone https://github.com/Silvafox76/python-tdd-bdd-automation-suite.git
cd python-tdd-bdd-automation-suite
🐍 Create virtual environment and install dependencies
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
🧪 Run Tests
Unit Tests (TDD)
bash
Copy
Edit
python -m unittest discover tests
Behavior-Driven Tests (BDD)
bash
Copy
Edit
behave
🐳 Docker Support
To build and run the app in Docker:

bash
Copy
Edit
docker build -t tdd-bdd-suite .
docker run -it tdd-bdd-suite
🧪 Sample Feature (BDD)
gherkin
Copy
Edit
Feature: Calculator Service
  Scenario: Add two numbers
    Given the calculator is running
    When I add 4 and 5
    Then the result should be 9
🤝 Contributing
Want to sharpen your TDD/BDD chops or expand the framework to other services? Pull requests are welcome!

📜 License
This project is licensed under the Apache 2.0 License. See the LICENSE file for details.

📣 Author
Ryan Dear
Senior IT Program/Project Manager | AI/ML Enthusiast | Cloud & DevOps Leader
LinkedIn • GitHub • Credly

“Testing isn't optional — it's the pulse check of professional software.”
