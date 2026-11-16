"""This module implements the Command Pattern for transaction execution and undo/redo."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from balance.balance import Balance
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class ITransactionCommand(ABC):
    """Abstract Base Class defining the Command interface."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass


class ApplyTransactionCommand(ITransactionCommand):
    """
    Concrete command that encapsulates applying a transaction to the balance.

    Demonstrates Dependency Injection by receiving the Balance and Transaction
    dependencies via constructor.
    """

    def __init__(self, balance: Balance, transaction: Transaction):
        """
        Initialize the command.

        Args:
            balance (Balance): The balance receiver instance.
            transaction (Transaction): The transaction to apply.
        """
        self.balance = balance
        self.transaction = transaction
        self.is_executed = False

    def execute(self) -> None:
        """Apply the transaction to the balance."""
        self.balance.apply_transaction(self.transaction)
        self.is_executed = True

    def undo(self) -> None:
        """
        Reverse the applied transaction on the balance and notify observers.

        Raises:
            RuntimeError: If attempting to undo an unexecuted command.
        """
        if not self.is_executed:
            raise RuntimeError("Cannot undo a command that has not been executed.")

        if self.transaction.category == TransactionCategory.INCOME:
            self.balance.add_expense(self.transaction.amount)
        elif self.transaction.category == TransactionCategory.EXPENSE:
            self.balance.add_income(self.transaction.amount)
        else:
            raise ValueError(f"Invalid transaction category: {self.transaction.category}")

        self.balance.notify_observers(self.transaction)
        self.is_executed = False

    def __repr__(self) -> str:
        return f"ApplyTransactionCommand(transaction={self.transaction}, executed={self.is_executed})"


class TransactionInvoker:
    """
    Invoker class that manages execution history, supporting undo and redo operations.
    """

    def __init__(self):
        """Initialize empty command history and redo stacks."""
        self._history: List[ITransactionCommand] = []
        self._redo_stack: List[ITransactionCommand] = []

    def execute_command(self, command: ITransactionCommand) -> None:
        """
        Execute a transaction command, records it in history, and clears redo stack.

        Args:
            command (ITransactionCommand): The command to execute.
        """
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()

    def undo(self) -> Optional[ITransactionCommand]:
        """
        Undo the most recently executed transaction command.

        Returns:
            ITransactionCommand | None: The undone command, or None if history is empty.
        """
        if not self._history:
            return None
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)
        return command

    def redo(self) -> Optional[ITransactionCommand]:
        """
        Redo the most recently undone transaction command.

        Returns:
            ITransactionCommand | None: The re-executed command, or None if redo stack is empty.
        """
        if not self._redo_stack:
            return None
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)
        return command

    @property
    def history(self) -> List[ITransactionCommand]:
        """Return a copy of the execution history."""
        return list(self._history)

    @property
    def redo_stack(self) -> List[ITransactionCommand]:
        """Return a copy of the redo stack."""
        return list(self._redo_stack)

    def can_undo(self) -> bool:
        """Check if an undo operation is available."""
        return len(self._history) > 0

    def can_redo(self) -> bool:
        """Check if a redo operation is available."""
        return len(self._redo_stack) > 0
