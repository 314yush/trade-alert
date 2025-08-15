"""
Trading Strategies Package

This package contains all trading strategies organized in a modular way.
Each strategy is a separate class that can be modified independently.
"""

from .base_strategy import BaseStrategy
from .aggressive_momentum import AggressiveMomentumStrategy
from .moderate_ema import ModerateEMAStrategy
from .conservative_trend import ConservativeTrendStrategy

__all__ = [
    'BaseStrategy',
    'AggressiveMomentumStrategy', 
    'ModerateEMAStrategy',
    'ConservativeTrendStrategy'
]
