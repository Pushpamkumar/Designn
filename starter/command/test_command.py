"""Unit tests for Command Pattern implementation (ApplyTransactionCommand & TransactionInvoker)."""

import unittest
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from command.transaction_command import ApplyTransactionCommand, TransactionInvoker


class TestTransactionCommand(unittest.TestCase):
    """Test suite for TransactionCommand and TransactionInvoker."""

    def setUp(self):
        """Set up a clean balance and invoker before each test."""
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.invoker = TransactionInvoker()

    def test_execute_income_command(self):
        """Verifies that executing an income command increases the balance."""
        txn = Transaction(100, TransactionCategory.INCOME)
        cmd = ApplyTransactionCommand(self.balance, txn)
        self.invoker.execute_command(cmd)

        self.assertEqual(self.balance.get_balance(), 100.0)
        self.assertEqual(len(self.invoker.history), 1)
        self.assertTrue(self.invoker.can_undo())
        self.assertFalse(self.invoker.can_redo())

    def test_execute_expense_command(self):
        """Verifies that executing an expense command deducts from the balance."""
        txn = Transaction(45, TransactionCategory.EXPENSE)
        cmd = ApplyTransactionCommand(self.balance, txn)
        self.invoker.execute_command(cmd)

        self.assertEqual(self.balance.get_balance(), -45.0)

    def test_undo_income_command(self):
        """Verifies that undoing an income command reverses the balance change."""
        txn = Transaction(150, TransactionCategory.INCOME)
        cmd = ApplyTransactionCommand(self.balance, txn)
        self.invoker.execute_command(cmd)
        self.assertEqual(self.balance.get_balance(), 150.0)

        undone = self.invoker.undo()
        self.assertIs(undone, cmd)
        self.assertEqual(self.balance.get_balance(), 0.0)
        self.assertFalse(self.invoker.can_undo())
        self.assertTrue(self.invoker.can_redo())

    def test_undo_expense_command(self):
        """Verifies that undoing an expense command restores the balance."""
        txn = Transaction(80, TransactionCategory.EXPENSE)
        cmd = ApplyTransactionCommand(self.balance, txn)
        self.invoker.execute_command(cmd)
        self.assertEqual(self.balance.get_balance(), -80.0)

        self.invoker.undo()
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_redo_command(self):
        """Verifies that redoing an undone command reapplies it to the balance."""
        txn = Transaction(200, TransactionCategory.INCOME)
        cmd = ApplyTransactionCommand(self.balance, txn)
        self.invoker.execute_command(cmd)
        self.invoker.undo()
        self.assertEqual(self.balance.get_balance(), 0.0)

        redone = self.invoker.redo()
        self.assertIs(redone, cmd)
        self.assertEqual(self.balance.get_balance(), 200.0)
        self.assertTrue(self.invoker.can_undo())
        self.assertFalse(self.invoker.can_redo())

    def test_undo_on_empty_history(self):
        """Verifies that undo on empty history safely returns None."""
        result = self.invoker.undo()
        self.assertIsNone(result)

    def test_redo_on_empty_stack(self):
        """Verifies that redo on empty redo stack safely returns None."""
        result = self.invoker.redo()
        self.assertIsNone(result)

    def test_undo_unexecuted_command_raises(self):
        """Verifies that attempting to undo an unexecuted command raises RuntimeError."""
        txn = Transaction(50, TransactionCategory.INCOME)
        cmd = ApplyTransactionCommand(self.balance, txn)
        with self.assertRaises(RuntimeError):
            cmd.undo()

    def test_new_command_clears_redo_stack(self):
        """Verifies that executing a new command clears the redo history."""
        cmd1 = ApplyTransactionCommand(self.balance, Transaction(100, TransactionCategory.INCOME))
        cmd2 = ApplyTransactionCommand(self.balance, Transaction(50, TransactionCategory.INCOME))

        self.invoker.execute_command(cmd1)
        self.invoker.undo()
        self.assertTrue(self.invoker.can_redo())

        # Executing a new command should discard pending redos
        self.invoker.execute_command(cmd2)
        self.assertFalse(self.invoker.can_redo())
        self.assertEqual(self.balance.get_balance(), 50.0)

    def test_command_triggers_observer_alerts(self):
        """Verifies that observers react during both command execution and undo."""
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        # Apply income: balance = 100, no alert
        cmd_inc = ApplyTransactionCommand(self.balance, Transaction(100, TransactionCategory.INCOME))
        self.invoker.execute_command(cmd_inc)
        self.assertFalse(observer.alert_triggered)

        # Apply expense: balance = 30, alert triggers
        cmd_exp = ApplyTransactionCommand(self.balance, Transaction(70, TransactionCategory.EXPENSE))
        self.invoker.execute_command(cmd_exp)
        self.assertTrue(observer.alert_triggered)

        # Undo expense: balance = 100, alert clears
        self.invoker.undo()
        self.assertFalse(observer.alert_triggered)


if __name__ == "__main__":
    unittest.main()
