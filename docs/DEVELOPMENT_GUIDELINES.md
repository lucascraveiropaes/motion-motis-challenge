# Team Development Standards & PR Guidelines

This document outlines the mandatory standards for all developers contributing to the **motis-challenge** project. These rules ensure code quality, maintainability, and a smooth review process.

---

## 1. Code Quality & Testing

### 1.1 Code Coverage
*   **Minimum Threshold:** All new features and bug fixes must maintain a minimum of **80% code coverage**.
*   **Critical Logic:** Core business logic (found in `packages/`) should aim for **95%+ coverage**.
*   **Validation:** Use `just test` (which triggers `pytest --cov`) before pushing any code.

### 1.2 Linting & Formatting
*   **Strict Adherence:** We use **Ruff** for both linting and formatting.
*   **Automation:** Always run `just format` and `just lint` before committing.
*   **Type Hints:** All function signatures must include Python type hints. Avoid `Any` whenever possible.

---

## 2. Pull Request (PR) Standards

A PR is not just a code drop; it's a communication tool. Every PR must follow this template:

### 2.1 PR Template
```markdown
## 🎯 Purpose
Briefly explain *what* this PR does and *why* it is necessary. Link to any related issues/tickets.

## 🛠️ Implementation Details
- Describe the technical approach.
- List any new dependencies added.
- Mention any architectural changes (e.g., new tables, shared packages).

## 🧪 Testing Performed
- [ ] Unit tests passed (list key tests).
- [ ] Integration tests passed (e.g., FastAPI endpoints).
- [ ] Manual validation (e.g., "Tested via Postman/cURL").

## 📸 Proof of Work (Optional but Recommended)
- Attach screenshots of API responses.
- For CLI/Background tasks, paste a snippet of the logs.
- Loom/Video links for complex logic flow.
```

---

## 3. Branching & Commits

### 3.1 Conventional Commits
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
*   `feat: ...` for new features.
*   `fix: ...` for bug fixes.
*   `docs: ...` for documentation changes.
*   `test: ...` for adding/fixing tests.
*   `refactor: ...` for code changes that neither fix a bug nor add a feature.

### 3.2 Branch Naming
*   `feature/short-description`
*   `bugfix/issue-id-short-description`
*   `hotfix/urgent-fix-description`

---

## 4. Documentation & Comments

*   **Self-Documenting Code:** Prioritize clear variable/function names over comments.
*   **Docstrings:** Use Google-style docstrings for all public classes and functions in `packages/`.
*   **The "Why", not the "What":** Use comments to explain complex or non-obvious logic, not to describe what the code is literally doing.

---

## 5. Peer Review Process

1.  **Self-Review:** Before requesting a review, read through your own diff on GitHub/ADO.
2.  **Justfile Check:** Ensure `just lint` and `just test` pass in the CI environment (or locally if CI is pending).
3.  **Constructive Feedback:** Reviewers should focus on logic, security, and architecture. Minor style issues should be handled by the linter.
