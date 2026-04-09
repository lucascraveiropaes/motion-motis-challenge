# Project FinGuard

## Project Overview
FinGuard is an automated financial assistant designed to process raw bank transaction descriptions, classify them into meaningful categories (e.g., "Food", "Subscriptions", "Salary"), and potentially detect fraudulent patterns. The system is architected into two main parts:
1.  **Shared Logic (`packages/transaction-engine`)**: This core library encapsulates the transaction classification rules and data sanitization. It includes a `TransactionClassifier` class responsible for managing transaction categories (CRUD operations) and performing the actual classification based on these categories. Categories are persisted in an SQLite database (`categories.db`) within this package.
2.  **Service Layer (`application-agents/classifier-agent`)**: A FastAPI-based agent that serves as the entry point for receiving transaction descriptions. It utilizes the `transaction-engine` to classify these descriptions and persists an audit log of all classification requests and their results into its own SQLite database (`classifier.db`).

## Technologies
-   **Language**: Python 3.13+
-   **Package Management**: `uv` (for package management and workspaces)
-   **Task Automation**: `just` (for standard development commands)
-   **Web Framework**: FastAPI
-   **ORM**: SQLAlchemy (for database interactions with SQLite)

## Building and Running

The project utilizes `uv` for dependency management and `just` for common development tasks.

*   **Install Dependencies**:
    ```bash
    just install
    ```
*   **Run Linting and Formatting**:
    ```bash
    just lint
    ```
*   **Run Tests with Coverage**:
    ```bash
    just test
    ```
*   **Start the Classifier Agent in Development Mode**:
    ```bash
    just dev
    ```

## Development Conventions

The project adheres to the following development standards:

*   **Code Coverage**: Aim for a minimum of 80% code coverage for all new features and bug fixes, with core business logic (`packages/`) targeting 95%+.
*   **Linting & Formatting**: Uses `Ruff` for strict adherence to linting and formatting rules. Always run `just lint` before committing.
*   **Type Hints**: All Python function signatures must include type hints, avoiding `Any` where possible.
*   **Pull Request (PR) Standards**: Follows a structured PR template including purpose, implementation details, testing performed, and optional proof of work.
*   **Branching & Commits**: Adheres to [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`) and standard branch naming conventions (`feature/`, `bugfix/`, `hotfix/`).
*   **Documentation & Comments**: Prioritizes self-documenting code. Requires Google-style docstrings for all public classes and functions in `packages/`. Comments should explain the "why" behind complex logic, not just "what" the code does.

## Key Components

### `transaction-engine`
-   **Location**: `finguard-workspace/packages/transaction-engine/`
-   **Purpose**: Contains the core classification logic.
-   **Key Files**:
    -   `src/transaction_engine/classifier.py`: Implements the `TransactionClassifier` class with CRUD for categories and the `classify_transaction(description: str) -> str` method. Categories are persisted in `categories.db`.
    -   `pyproject.toml`: Manages package-specific dependencies, including `sqlalchemy`.

### `classifier-agent`
-   **Location**: `finguard-workspace/application-agents/classifier-agent/`
-   **Purpose**: FastAPI service for transaction classification.
-   **Key Files**:
    -   `src/classifier_agent/app.py`: Defines the FastAPI application, including the `/transactions/classify` endpoint which uses the `transaction-engine` and persists transaction records in `classifier.db`.
    -   `src/classifier_agent/models.py`: Defines the SQLAlchemy model for `TransactionRecord` for auditing purposes.
    -   `pyproject.toml`: Manages FastAPI and SQLAlchemy dependencies for the agent.
