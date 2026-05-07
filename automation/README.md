# Notes App — UI + API Hybrid Automation Suite
### Capstone Project | Selenium · Python · Pytest

---

## Project Structure

```
notes_automation/
├── tests/
│   ├── ui/          # Selenium UI tests (login, create note, validations)
│   ├── api/         # API automation (GET, POST, DELETE, negative)
│   └── e2e/         # Hybrid E2E flows (UI↔API sync)
├── pages/           # Page Object Model classes
├── api_client/      # Reusable authenticated API clients
├── fixtures/        # Pytest fixtures (browser, API session)
├── config/          # config.yaml + environment.py singleton
├── utils/           # logger, screenshot, retry, performance, self-healing
├── conftest.py      # Root conftest with hooks
├── pytest.ini       # Pytest configuration
├── Jenkinsfile      # CI/CD pipeline
└── requirements.txt
```

---

## Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd notes_automation

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials
```bash
cp .env.example .env
# Edit .env with your test account credentials
```

> **Note:** Register a free test account at  
> https://practice.expandtesting.com/notes/app/register

### 3. Run All Tests
```bash
pytest
```

### 4. Run by Marker
```bash
pytest -m ui       # UI tests only
pytest -m api      # API tests only
pytest -m e2e      # Hybrid E2E only
pytest -m smoke    # Smoke suite
pytest -m negative # Negative/error tests
```

### 5. Run in Parallel
```bash
# 4 workers for API tests (fastest, no browser)
pytest tests/api -n 4

# 2 workers for UI (browser-heavy)
pytest tests/ui -n 2

# All tests parallelized
pytest -n auto
```

---

## Allure Report

### Install Allure CLI (macOS)
```bash
brew install allure
```

### Install Allure CLI (Windows/Linux)
```bash
# Download from: https://github.com/allure-framework/allure2/releases
# Add to PATH
```

### Generate & Serve
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

---

## CI/CD — Jenkins

1. Install plugins: **Allure Jenkins Plugin**, **Pipeline**
2. Add credentials `notes-test-email` and `notes-test-password`
3. Create a Pipeline job pointing to `Jenkinsfile`

Pipeline stages:
```
Checkout → Setup Python → Lint → [UI Tests ∥ API Tests] → E2E Tests → Allure Report → Archive
```

---

## Key Design Decisions

| Concern | Solution |
|---|---|
| Flaky UI actions | `@retry_on_flaky` decorator (tenacity) |
| Stale locators | `self_healing.py` — 4-level fallback strategy |
| Performance | `measure_time()` context manager — assert < 2s |
| Parallel isolation | `scope="function"` fixtures, no shared state |
| Cross-browser | `BROWSER=firefox` env var — Chrome default |
| Headless CI | `HEADLESS=true` env var |
| Screenshot on fail | `hookimpl tryfirst` + allure attachment |

---

## MCP / AI-Assisted Features (Section 3.4)

The `utils/self_healing.py` module implements locator self-healing locally.  
For LLM-assisted capabilities, integrate with the Anthropic API:

```python
# Example: ask Claude to suggest a better locator
import anthropic
client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=256,
    messages=[{
        "role": "user",
        "content": f"Suggest a stable CSS selector for a button with text 'Save Note' in a React SPA."
    }]
)
print(msg.content[0].text)
```

Use cases:
- **Test data generation**: Prompt Claude for realistic note titles/descriptions
- **Failure analysis**: Send error logs to Claude for root cause suggestions
- **Locator improvement**: Ask Claude to suggest attribute-based selectors

---

## Requirements

- Python 3.10+
- Google Chrome (latest) or Firefox
- ChromeDriver / GeckoDriver (auto-managed via webdriver-manager)
- Allure 2.x (for reports)
- Jenkins (for CI/CD)
