"""This module implements the Strategy Pattern for financial budget planning."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict


class IBudgetStrategy(ABC):
    """Abstract Strategy interface for budget allocation."""

    @abstractmethod
    def calculate_allocation(self, total_income: float) -> Dict[str, float]:
        """
        Calculate budget allocation based on total income.

        Args:
            total_income (float): The total income to allocate.

        Returns:
            Dict[str, float]: Categorized budget amounts.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the budgeting strategy."""
        pass


class FiftyThirtyTwentyStrategy(IBudgetStrategy):
    """
    50/30/20 Rule:
    - 50% Needs (Essential expenses)
    - 30% Wants (Discretionary spending)
    - 20% Savings (Emergency fund, investments, debt repayment)
    """

    def calculate_allocation(self, total_income: float) -> Dict[str, float]:
        income = max(0.0, float(total_income))
        return {
            "Needs (50%)": round(income * 0.50, 2),
            "Wants (30%)": round(income * 0.30, 2),
            "Savings & Investments (20%)": round(income * 0.20, 2),
        }

    def get_name(self) -> str:
        return "50/30/20 Rule"


class ZeroBasedBudgetStrategy(IBudgetStrategy):
    """
    Zero-Based Budgeting Strategy:
    Assigns every single dollar a dedicated financial purpose:
    - 35% Housing & Utilities
    - 25% Food & Essentials
    - 15% Emergency Savings
    - 15% Long-term Investments
    - 10% Discretionary
    """

    def calculate_allocation(self, total_income: float) -> Dict[str, float]:
        income = max(0.0, float(total_income))
        return {
            "Housing & Utilities (35%)": round(income * 0.35, 2),
            "Food & Essentials (25%)": round(income * 0.25, 2),
            "Emergency Savings (15%)": round(income * 0.15, 2),
            "Long-term Investments (15%)": round(income * 0.15, 2),
            "Discretionary (10%)": round(income * 0.10, 2),
        }

    def get_name(self) -> str:
        return "Zero-Based Budgeting"


class BudgetPlanner:
    """
    Context class for budgeting strategies.
    
    Demonstrates Dependency Injection by accepting an IBudgetStrategy instance
    via constructor or setter method.
    """

    def __init__(self, strategy: IBudgetStrategy):
        """
        Initialize the planner with an injected budgeting strategy.

        Args:
            strategy (IBudgetStrategy): The strategy algorithm to use.
        """
        self._strategy = strategy

    @property
    def strategy(self) -> IBudgetStrategy:
        """Return current strategy."""
        return self._strategy

    def set_strategy(self, strategy: IBudgetStrategy) -> None:
        """
        Dynamically switch the budgeting strategy at runtime.

        Args:
            strategy (IBudgetStrategy): The new strategy to use.
        """
        self._strategy = strategy

    def plan(self, total_income: float) -> Dict[str, float]:
        """
        Execute the current strategy to allocate income.

        Args:
            total_income (float): Total income amount to allocate.

        Returns:
            Dict[str, float]: The calculated budget allocation.
        """
        return self._strategy.calculate_allocation(total_income)
