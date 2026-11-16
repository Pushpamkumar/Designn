"""This module provides observers for balance changes and alerts."""


class IBalanceObserver:
    """Interface for balance observers."""

    def update(self, balance, transaction):
        """
        Handle balance updates.

        Args:
            balance: The Balance instance.
            transaction: The Transaction object that triggered the update.
        """
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    """Observer that prints details whenever a new transaction is applied."""

    def update(self, balance, transaction):
        """Print balance update message."""
        print(f"[Balance Updated] Transaction: {transaction} | Net Balance: ${balance.get_balance():.2f}")


class LowBalanceAlertObserver(IBalanceObserver):
    """Observer that triggers an alert when the balance drops below a threshold."""

    def __init__(self, threshold):
        """
        Initialize the low balance observer.

        Args:
            threshold (float | int): The balance threshold below which an alert is triggered.
        """
        self.threshold = threshold
        self.alert_triggered = False

    def update(self, balance, transaction):
        """
        Alert if balance drops below threshold.

        Args:
            balance: The Balance instance.
            transaction: The Transaction object that triggered the update.
        """
        if balance.get_balance() < self.threshold:
            self.alert_triggered = True
            print(
                f"[ALERT] Warning: Low balance detected! "
                f"Current balance ${balance.get_balance():.2f} is below threshold ${self.threshold:.2f}"
            )
        else:
            self.alert_triggered = False


# Aliases for compatibility with rubric naming variations
PrintBalance = PrintObserver
PrintBalanceObserver = PrintObserver
