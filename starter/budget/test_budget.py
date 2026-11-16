"""Unit tests for Strategy Pattern implementation (Budget Strategies & BudgetPlanner)."""

import unittest
from budget.budget_strategy import (
    FiftyThirtyTwentyStrategy,
    ZeroBasedBudgetStrategy,
    BudgetPlanner,
)


class TestBudgetStrategy(unittest.TestCase):
    """Test suite for budget planning strategies."""

    def test_fifty_thirty_twenty_strategy(self):
        """Verifies 50/30/20 budget breakdown."""
        strategy = FiftyThirtyTwentyStrategy()
        planner = BudgetPlanner(strategy)
        allocation = planner.plan(1000.0)

        self.assertEqual(allocation["Needs (50%)"], 500.0)
        self.assertEqual(allocation["Wants (30%)"], 300.0)
        self.assertEqual(allocation["Savings & Investments (20%)"], 200.0)
        self.assertEqual(sum(allocation.values()), 1000.0)

    def test_zero_based_budget_strategy(self):
        """Verifies zero-based budget distribution."""
        strategy = ZeroBasedBudgetStrategy()
        planner = BudgetPlanner(strategy)
        allocation = planner.plan(2000.0)

        self.assertEqual(allocation["Housing & Utilities (35%)"], 700.0)
        self.assertEqual(allocation["Food & Essentials (25%)"], 500.0)
        self.assertEqual(allocation["Emergency Savings (15%)"], 300.0)
        self.assertEqual(allocation["Long-term Investments (15%)"], 300.0)
        self.assertEqual(allocation["Discretionary (10%)"], 200.0)
        self.assertEqual(sum(allocation.values()), 2000.0)

    def test_dynamic_strategy_switching(self):
        """Verifies strategy can be changed at runtime via dependency injection."""
        strat1 = FiftyThirtyTwentyStrategy()
        strat2 = ZeroBasedBudgetStrategy()
        planner = BudgetPlanner(strat1)

        self.assertEqual(planner.strategy.get_name(), "50/30/20 Rule")
        planner.set_strategy(strat2)
        self.assertEqual(planner.strategy.get_name(), "Zero-Based Budgeting")

        alloc = planner.plan(1000.0)
        self.assertIn("Housing & Utilities (35%)", alloc)

    def test_zero_and_negative_income_handling(self):
        """Verifies that non-positive income handles gracefully without errors."""
        strategy = FiftyThirtyTwentyStrategy()
        planner = BudgetPlanner(strategy)
        alloc_zero = planner.plan(0.0)
        self.assertEqual(alloc_zero["Needs (50%)"], 0.0)

        alloc_neg = planner.plan(-500.0)
        self.assertEqual(alloc_neg["Needs (50%)"], 0.0)


if __name__ == "__main__":
    unittest.main()
