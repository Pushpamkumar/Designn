"""This module defines the TransactionAdapter class to adapt third-party transactions."""

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TransactionAdapter:
    """
    Adapter pattern implementation.

    Converts external third-party transactions (e.g. ExternalFreelanceIncome)
    into standard internal Transaction objects compatible with Balance.
    """

    def __init__(self, external_transaction):
        """
        Initialize the adapter with an external transaction object.

        Args:
            external_transaction: The external transaction to adapt.
        """
        self.external_transaction = external_transaction

    def to_transaction(self):
        """
        Convert an external transaction to a standard Transaction object.

        Returns:
            Transaction: An internal Transaction instance with standard amount and category.
        """
        typ = getattr(self.external_transaction, "typ", "income")
        if str(typ).lower() == "income":
            category = TransactionCategory.INCOME
        elif str(typ).lower() == "expense":
            category = TransactionCategory.EXPENSE
        else:
            category = TransactionCategory.INCOME

        return Transaction(self.external_transaction.amount, category)
