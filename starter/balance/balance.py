"""This module provides the Singleton Balance class to track financial balance."""

from transaction.transaction_category import TransactionCategory


class Balance:
    """
    Singleton class to manage and track the account balance.

    Ensures that a single source of truth for the balance exists across the application.
    Supports registering and notifying balance observers.
    """

    _instance = None

    def __init__(self):
        """
        Initialize the balance. Direct instantiation is prevented.
        Use Balance.get_instance() to obtain the singleton instance.
        """
        raise RuntimeError("Direct instantiation is not allowed. Use Balance.get_instance() instead.")

    @classmethod
    def get_instance(cls):
        """
        Retrieve or initialize the singleton instance of Balance.

        Returns:
            Balance: The shared Balance instance.
        """
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance._balance = 0.0
            cls._instance._observers = []
        return cls._instance

    def reset(self):
        """Reset the net balance to zero and clear registered observers."""
        self._balance = 0.0
        self._observers.clear()

    def add_income(self, amount):
        """
        Add income to the balance.

        Args:
            amount (float | int): The income amount to add.
        """
        self._balance += amount

    def add_expense(self, amount):
        """
        Subtract expense from the balance.

        Args:
            amount (float | int): The expense amount to deduct.
        """
        self._balance -= amount

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance and notify observers.

        Args:
            transaction (Transaction): The transaction to apply.

        Raises:
            ValueError: If the transaction category is invalid.
        """
        if transaction.category == TransactionCategory.INCOME:
            self.add_income(transaction.amount)
        elif transaction.category == TransactionCategory.EXPENSE:
            self.add_expense(transaction.amount)
        else:
            raise ValueError(f"Invalid transaction category: {transaction.category}")

        self.notify_observers(transaction)

    def register_observer(self, observer):
        """
        Register an observer to receive balance update notifications.

        Args:
            observer: The observer implementing an update method.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer):
        """
        Unregister an observer from receiving notifications.

        Args:
            observer: The observer to unregister.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, transaction):
        """
        Notify all registered observers about the balance update.

        Args:
            transaction: The transaction that caused the balance update.
        """
        for observer in list(self._observers):
            observer.update(self, transaction)

    def get_balance(self):
        """
        Get the current net balance.

        Returns:
            float: The net balance.
        """
        return self._balance

    def summary(self):
        """
        Return a summary string of the net balance.

        Returns:
            str: Human-readable balance summary.
        """
        return f"Current Balance: ${self._balance:.2f}"
