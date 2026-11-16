 # Personal Finance Manager — Object-Oriented Design Patterns

A modular, extensible, and robust personal finance management application written in Python. This project demonstrates classic Object-Oriented Design Patterns across creational, structural, and behavioral categories, augmented by Dependency Injection to maximize testability, maintainability, and clean architectural separation.

---

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [Design Patterns Implemented](#design-patterns-implemented)
  - [1. Singleton Pattern (Creational)](#1-singleton-pattern-creational)
  - [2. Adapter Pattern (Structural)](#2-adapter-pattern-structural)
  - [3. Observer Pattern (Behavioral)](#3-observer-pattern-behavioral)
  - [4. Command Pattern with Undo/Redo (Behavioral - Student's Choice)](#4-command-pattern-with-undoredo-behavioral---students-choice)
  - [Bonus: Strategy Pattern for Budget Allocation](#bonus-strategy-pattern-for-budget-allocation)
- [Dependency Injection & Modularity](#dependency-injection--modularity)
- [Design Trade-offs & Engineering Reflection](#design-trade-offs--engineering-reflection)
- [Directory Structure](#directory-structure)
- [Installation & Execution](#installation--execution)
- [Unit Testing Suite](#unit-testing-suite)
- [Code Quality & PEP 8 Standards](#code-quality--pep-8-standards)

---

## Architectural Overview

The application provides core personal finance tracking: recording incomes, logging expenses, observing real-time balance fluctuations, alerting users to critically low funds, supporting reversible operations (undo/redo), and calculating personalized financial allocations.

Rather than implementing business logic in a procedural or tightly-coupled manner, the application is partitioned into decoupled domain packages (`balance`, `transaction`, `command`, and `budget`), each adhering strictly to the **Single Responsibility Principle (SRP)** and the **Open/Closed Principle (OCP)**.

---

## Design Patterns Implemented

### 1. Singleton Pattern (Creational)
- **Module**: `balance/balance.py` (`Balance` class)
- **Intent**: Ensure that exactly one shared instance of `Balance` exists throughout the runtime lifecycle, providing a single source of truth for the account's financial state.
- **Implementation Highlights**:
  - Direct instantiation via `Balance()` is strictly prohibited by raising a `RuntimeError`.
  - A thread-safe class method `Balance.get_instance()` manages lazy instantiation and guarantees instance identity (`balance1 is balance2`).
  - Includes a `reset()` method designed specifically for test isolation, resetting the numeric balance to `0.0` and clearing registered observers between test executions.
- **Why It Was Chosen**: Financial tracking requires that income and expense mutations reflect against one unified account state. Allowing multiple disparate balance objects would introduce synchronization bugs, orphaned transactions, and data inconsistency.

### 2. Adapter Pattern (Structural)
- **Module**: `transaction/transaction_adapter.py` (`TransactionAdapter` class)
- **Intent**: Translate third-party or heterogeneous transaction representations into the standardized internal `Transaction` format required by the balance manager.
- **Implementation Highlights**:
  - Receives an `ExternalFreelanceIncome` object (which carries freelance-specific metadata such as `invoice_id`, `description`, and raw string types).
  - Normalizes the external attributes and converts them into an internal `Transaction` typed with `TransactionCategory.INCOME`.
- **Why It Was Chosen**: External services (freelance portals, banking APIs, invoice systems) define their own data contracts. The Adapter pattern shields our core business model from foreign schema churn, enabling plug-and-play support for future payment providers without altering domain logic.

### 3. Observer Pattern (Behavioral)
- **Module**: `balance/balance_observer.py` (`IBalanceObserver`, `PrintObserver` / `PrintBalance`, `LowBalanceAlertObserver`)
- **Intent**: Establish a one-to-many dependency relationship so that when the financial balance changes, all subscribed listeners are automatically notified and updated.
- **Implementation Highlights**:
  - `IBalanceObserver` specifies the abstract contract `update(balance, transaction)`.
  - `PrintObserver` (aliased as `PrintBalance` / `PrintBalanceObserver`) logs real-time ledger activity upon every applied transaction.
  - `LowBalanceAlertObserver` monitors the net balance against a configurable monetary threshold (e.g., $100.00 or $50.00), automatically toggling `alert_triggered` and printing an urgent alert if balance drops below threshold.
- **Why It Was Chosen**: Directly coupling alerting and console printing into `Balance` would violate the Single Responsibility and Open/Closed principles. With Observer, developers can introduce SMS, email, or database logging observers without touching `Balance`.

### 4. Command Pattern with Undo/Redo (Behavioral - Student's Choice)
- **Module**: `command/transaction_command.py` (`ITransactionCommand`, `ApplyTransactionCommand`, `TransactionInvoker`)
- **Intent**: Encapsulate transaction execution requests as discrete command objects, decoupling the request invoker from the target balance receiver and enabling reversible transaction workflows (Undo and Redo).
- **Implementation Highlights**:
  - `ApplyTransactionCommand` encapsulates a `Balance` receiver and a `Transaction` payload. Its `execute()` method applies the transaction, and its `undo()` method computes and executes the exact inverse financial action while updating all registered observers.
  - `TransactionInvoker` acts as the invoker, retaining an execution history list and a redo stack. It provides `execute_command()`, `undo()`, `redo()`, `can_undo()`, and `can_redo()` methods.
- **Why It Was Chosen**: Financial systems must be resilient against accidental transactions, erroneous entries, and auditing requirements. The Command pattern elevates actions into first-class objects, providing an audit trail, non-destructive rollbacks, and multi-step transaction replay.

### Bonus: Strategy Pattern for Budget Allocation
- **Module**: `budget/budget_strategy.py` (`IBudgetStrategy`, `FiftyThirtyTwentyStrategy`, `ZeroBasedBudgetStrategy`, `BudgetPlanner`)
- **Intent**: Define a family of budgeting algorithms, encapsulate each one, and make them interchangeable at runtime.
- **Implementation Highlights**:
  - `FiftyThirtyTwentyStrategy`: Allocates 50% to Needs, 30% to Wants, and 20% to Savings/Investments.
  - `ZeroBasedBudgetStrategy`: Directs 100% of available funds across Housing (35%), Essentials (25%), Emergency Savings (15%), Long-term Investments (15%), and Discretionary (10%).
  - `BudgetPlanner`: Serves as the strategy context, accepting strategies via constructor injection and supporting runtime switching with `set_strategy()`.
- **Why It Was Chosen**: Different users require distinct financial management methodologies. Hardcoding a single budgeting formula limits application utility. Strategy lets users dynamically pick or swap budgeting rules based on financial goals.

---

## Dependency Injection & Modularity

Dependency Injection (DI) is applied throughout the codebase to eliminate rigid coupling:

1. **Command Receiver & Payload Injection**: `ApplyTransactionCommand(balance, transaction)` receives the target `Balance` receiver and the specific `Transaction` via constructor arguments rather than referencing static globals. This allows mock receivers in test suites.
2. **Strategy Injection**: `BudgetPlanner(strategy)` accepts any implementation of `IBudgetStrategy`. New budgeting paradigms can be injected seamlessly without modifying the planner.
3. **External Source Injection**: `TransactionAdapter(external_transaction)` takes arbitrary external sources via constructor parameters, enabling flexible adaptation of heterogeneous input objects.
4. **Observer Registration Injection**: Observers are instantiated independently and injected into `Balance.register_observer(observer)`, decoupling alert policies and display formats from the subject.

---

## Design Trade-offs & Engineering Reflection

During the design and construction of this personal finance manager, several critical engineering trade-offs were evaluated:

### 1. Singleton State Management vs. Test Independence
* **Challenge**: The Singleton pattern introduces shared state across tests. When multiple unit tests mutate the singleton instance, state pollution can cause order-dependent test failures.
* **Resolution**: We engineered an explicit `reset()` method on `Balance` that resets the net balance to zero and purges all registered observers. Each test suite invokes `reset()` inside `setUp()`, guaranteeing test hermeticity and predictable execution.

### 2. Adapter Granularity vs. Schema Evolution
* **Challenge**: Third-party freelance data structures can vary widely across invoice providers. A rigid adapter risks throwing `AttributeError` when external fields change.
* **Resolution**: The adapter leverages defensive attribute access (`getattr(self.external_transaction, "typ", "income")`) with sensible fallbacks to safely map third-party structures to standard internal categories while keeping domain models clean.

### 3. Observer Synchronization vs. Performance
* **Challenge**: In a synchronous Observer pattern, slow or blocking observers (such as network or disk calls) could delay transaction processing.
* **Resolution**: Observers in this design maintain lightweight update handlers. For production deployments, this can readily be upgraded to asynchronous pub/sub queues (e.g., Celery, RabbitMQ) without changing the `IBalanceObserver` interface contract.

### 4. Command Inversion Accuracy vs. Memory Consumption
* **Challenge**: Retaining complete command histories consumes memory over extended application runtimes, and inverse operations (undoing) must account for edge cases such as already-triggered low-balance alerts.
* **Resolution**: The `ApplyTransactionCommand` directly mirrors inverse arithmetic on the receiver and immediately calls `balance.notify_observers()`. This triggers real-time observer state updates (for instance, clearing the low balance alert once an expense is undone).

---

## Directory Structure

```text
starter/
│
├── balance/
│   ├── __init__.py
│   ├── balance.py                 # Singleton Balance implementation
│   ├── balance_observer.py        # Observer interfaces and concrete observers
│   ├── test_balance.py            # Unit tests for Singleton Balance
│   └── test_balance_observer.py   # Unit tests for LowBalanceAlertObserver
│
├── transaction/
│   ├── __init__.py
│   ├── transaction.py             # Transaction domain model
│   ├── transaction_category.py    # TransactionCategory enum (INCOME, EXPENSE)
│   ├── external_income_transaction.py # Mock third-party freelance data
│   ├── transaction_adapter.py     # Adapter pattern implementation
│   ├── test_transaction.py        # Unit tests for Transaction class
│   └── test_transaction_adapter.py# Unit tests for TransactionAdapter
│
├── command/
│   ├── __init__.py
│   ├── transaction_command.py     # Command pattern & TransactionInvoker (Undo/Redo)
│   └── test_command.py            # Unit tests for Command and Invoker
│
├── budget/
│   ├── __init__.py
│   ├── budget_strategy.py         # Strategy pattern for budget planning
│   └── test_budget.py             # Unit tests for budget strategies
│
└── main.py                        # Complete interactive simulation script
```

---

## Installation & Execution

### Prerequisites
- Python 3.9 or higher (Python 3.10+ recommended)

### Running the Application

Navigate to the `starter` directory and run the entry-point script:

```bash
cd starter
python main.py
```

### Expected Output
The simulation demonstrates:
1. Singleton initialization and observer registration.
2. Standard transaction creation.
3. Adapting an external freelance invoice into an internal transaction.
4. Applying transactions via the Command Invoker with real-time observer logging.
5. Triggering a low-balance warning when balance falls below the threshold.
6. Performing Undo and Redo operations, demonstrating reversible financial ledger mutations.
7. Calculating budget distributions across multiple interchangeable financial strategies.

---

## Unit Testing Suite

The project includes unit tests for all implemented classes, design patterns, and edge cases using Python’s built-in `unittest` framework.

### Run All Unit Tests
From the `starter/` directory, run:

```bash
python -m unittest discover -s . -v
```

### Running Individual Test Suites
```bash
# Balance and Observer tests
python -m unittest balance/test_balance.py
python -m unittest balance/test_balance_observer.py

# Transaction and Adapter tests
python -m unittest transaction/test_transaction.py
python -m unittest transaction/test_transaction_adapter.py

# Command Pattern (Undo/Redo) tests
python -m unittest command/test_command.py

# Budget Strategy tests
python -m unittest budget/test_budget.py
```

### Test Suite Summary
| Test Module | Coverage Description |
| :--- | :--- |
| `test_balance.py` | Validates singleton instance uniqueness, initial balance, income/expense arithmetic, reset behavior, and invalid category handling. |
| `test_balance_observer.py` | Confirms `LowBalanceAlertObserver` accurately triggers alerts upon crossing the threshold and clears when funds recover. |
| `test_transaction.py` | Tests transaction creation, formatted string representations, and value equality. |
| `test_transaction_adapter.py` | Verifies external third-party freelance objects are mapped into standard `Transaction` objects. |
| `test_command.py` | Thoroughly tests command execution, single and multi-step undo/redo, empty stack safety, observer notifications during undo, and unexecuted error guards. |
| `test_budget.py` | Validates 50/30/20 and Zero-Based budget calculation math, negative income edge cases, and runtime strategy switching. |

**Total Tests**: 27 passing tests (0 failures, 0 errors).

---

## Code Quality & PEP 8 Standards

- **PEP 8 Compliant**: Variable names, class definitions, function signatures, docstrings, and imports follow standard Python conventions.
- **Type Annotations**: Applied across modules with `__future__.annotations` compatibility for clean, forward-compatible type hinting.
- **Idiomatic Python**: Utilizes Enums, list comprehensions, properties, and explicit error handling without redundant or dead code.
