"""This module serves as the entry point for the personal finance manager application."""

from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver, PrintObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome
from command.transaction_command import ApplyTransactionCommand, TransactionInvoker
from budget.budget_strategy import (
    FiftyThirtyTwentyStrategy,
    ZeroBasedBudgetStrategy,
    BudgetPlanner,
)


def main():
    """Execute the simulation of the personal finance manager application."""
    print("=" * 65)
    print("   PERSONAL FINANCE MANAGER - DESIGN PATTERNS DEMONSTRATION")
    print("=" * 65)

    # 1. Singleton Balance Setup
    balance = Balance.get_instance()
    balance.reset()
    print(f"\n[1] Initialized Singleton Balance: {balance.summary()}")

    # 2. Register Observers (Observer Pattern & Dependency Injection)
    print("\n[2] Registering Observers (PrintObserver & LowBalanceAlertObserver)...")
    print_observer = PrintObserver()
    low_balance_observer = LowBalanceAlertObserver(threshold=100.0)

    balance.register_observer(print_observer)
    balance.register_observer(low_balance_observer)
    print("    Registered: PrintObserver")
    print(f"    Registered: LowBalanceAlertObserver (threshold: ${low_balance_observer.threshold:.2f})")

    # 3. Create Standard Internal Transactions
    print("\n[3] Creating Internal Transactions...")
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]
    for txn in transactions:
        print(f"    Created: {txn}")

    # 4. Create External Income Transaction (Adapter Pattern)
    print("\n[4] Adapting External Freelance Transaction (Adapter Pattern)...")
    freelance_income = ExternalFreelanceIncome(1200, "INV-98765", "Mobile App Project")
    print(
        f"    External Data: Invoice={freelance_income.invoice_id}, "
        f"Amount=${freelance_income.amount}, Desc='{freelance_income.description}'"
    )
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()
    print(f"    Adapted to Internal Transaction: {adapted_transaction}")

    all_transactions = transactions + [adapted_transaction]

    # 5. Apply Transactions via Command Pattern (Command Pattern & Dependency Injection)
    print("\n[5] Applying Transactions via Command Pattern (TransactionInvoker)...")
    invoker = TransactionInvoker()

    for txn in all_transactions:
        # Injected balance receiver and transaction payload into command
        command = ApplyTransactionCommand(balance=balance, transaction=txn)
        invoker.execute_command(command)

    print(f"\n---> {balance.summary()} <---")

    # 6. Low Balance Alert Simulation
    print("\n[6] Simulating Expense Triggering Low Balance Alert...")
    large_expense = Transaction(1350, TransactionCategory.EXPENSE)
    alert_command = ApplyTransactionCommand(balance=balance, transaction=large_expense)
    invoker.execute_command(alert_command)
    print(f"---> {balance.summary()} | Alert Active: {low_balance_observer.alert_triggered} <---")

    # 7. Undo/Redo Capability (Command Pattern Standout Feature)
    print("\n[7] Demonstrating Undo/Redo Capability (Command Pattern)...")
    print("    Undoing last transaction (large expense of $1350)...")
    invoker.undo()
    print(f"    After Undo: {balance.summary()} | Alert Active: {low_balance_observer.alert_triggered}")

    print("    Redoing last transaction...")
    invoker.redo()
    print(f"    After Redo: {balance.summary()} | Alert Active: {low_balance_observer.alert_triggered}")

    print("    Undoing again to restore healthy balance...")
    invoker.undo()
    print(f"    Current Restored Balance: {balance.summary()}")

    # 8. Budget Planning (Strategy Pattern Standout Feature)
    print("\n[8] Budget Planning Strategy Simulation (Strategy Pattern)...")
    total_income_pool = balance.get_balance()
    print(f"    Allocating Available Funds (${total_income_pool:.2f}):")

    # Strategy 1: 50/30/20 Rule
    planner = BudgetPlanner(FiftyThirtyTwentyStrategy())
    print(f"\n    Strategy A: {planner.strategy.get_name()}")
    for category, amount in planner.plan(total_income_pool).items():
        print(f"      - {category}: ${amount:.2f}")

    # Strategy 2: Zero-Based Budgeting (Runtime Strategy Switch)
    planner.set_strategy(ZeroBasedBudgetStrategy())
    print(f"\n    Strategy B: {planner.strategy.get_name()} (Switched at Runtime)")
    for category, amount in planner.plan(total_income_pool).items():
        print(f"      - {category}: ${amount:.2f}")

    print("\n" + "=" * 65)
    print("   SIMULATION COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    main()
