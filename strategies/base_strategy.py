"""
Base Strategy Class

All trading strategies inherit from this base class, ensuring consistent interface
and common functionality across all strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    This class defines the interface that all strategies must implement,
    ensuring consistency and making the system modular and maintainable.
    """
    
    def __init__(self, name: str, timeframe: str, description: str):
        """
        Initialize base strategy.
        
        Args:
            name (str): Strategy name
            timeframe (str): Timeframe for this strategy
            description (str): Strategy description
        """
        self.name = name
        self.timeframe = timeframe
        self.description = description
        self.last_check_time = None
        self.last_signal_time = None
        self.signals_generated = 0
        
        logger.info(f"Initialized {self.name} strategy ({timeframe})")
    
    @abstractmethod
    def check_signal(self, symbol: str, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Check for trading signals (must be implemented by subclasses).
        
        Args:
            symbol (str): Trading pair symbol
            data (pd.DataFrame): Market data for analysis
            
        Returns:
            Optional[Dict[str, Any]]: Trading signal if conditions met, None otherwise
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters (must be implemented by subclasses).
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        pass
    
    def validate_data(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validate that required data columns are present.
        
        Args:
            data (pd.DataFrame): Data to validate
            required_columns (List[str]): Required column names
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        if data is None or data.empty:
            logger.warning(f"{self.name}: No data provided")
            return False
        
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            logger.warning(f"{self.name}: Missing columns: {missing_columns}")
            return False
        
        return True
    
    def format_signal(self, signal_type: str, symbol: str, price: float, 
                     stop_loss: float, take_profit: float, **kwargs) -> Dict[str, Any]:
        """
        Format a trading signal consistently across all strategies.
        
        Args:
            signal_type (str): 'long' or 'short'
            symbol (str): Trading pair
            price (float): Entry price
            stop_loss (float): Stop loss price
            take_profit (float): Take profit price
            **kwargs: Additional signal parameters
            
        Returns:
            Dict[str, Any]: Formatted trading signal
        """
        signal = {
            'profile': self.name,
            'strategy': self.description,
            'signal_type': signal_type,
            'symbol': symbol,
            'timeframe': self.timeframe,
            'price': price,
            'timestamp': datetime.now(),
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'generated_by': self.__class__.__name__
        }
        
        # Add any additional parameters
        signal.update(kwargs)
        
        # Update statistics
        self.last_signal_time = datetime.now()
        self.signals_generated += 1
        
        return signal
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get strategy statistics.
        
        Returns:
            Dict[str, Any]: Strategy statistics
        """
        return {
            'name': self.name,
            'timeframe': self.timeframe,
            'last_check_time': self.last_check_time,
            'last_signal_time': self.last_signal_time,
            'signals_generated': self.signals_generated
        }
    
    def reset_statistics(self) -> None:
        """Reset strategy statistics."""
        self.last_check_time = None
        self.last_signal_time = None
        self.signals_generated = 0
        logger.info(f"Reset statistics for {self.name}")
    
    def cleanup(self) -> None:
        """Clean up strategy resources."""
        logger.info(f"Cleaned up {self.name} strategy")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.timeframe})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', timeframe='{self.timeframe}')"
