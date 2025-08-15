"""
Conservative Trend Rider Strategy

Long-term trend following strategy using SMA crossovers with ADX and RSI confirmation.
This strategy can be modified independently without affecting other strategies.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import logging
from .base_strategy import BaseStrategy
from config import CONSERVATIVE_TREND_RIDER

logger = logging.getLogger(__name__)


class ConservativeTrendStrategy(BaseStrategy):
    """
    Conservative Trend Rider Strategy (4-hour timeframe).
    
    Long-term trend following strategy that looks for:
    - Golden Cross (50 SMA above 200 SMA) / Death Cross
    - ADX trend strength confirmation
    - RSI momentum validation
    - Multiple timeframe confirmation
    """
    
    def __init__(self):
        """Initialize the conservative trend strategy."""
        super().__init__(
            name="Conservative Trend Rider",
            timeframe="4h",
            description="Enhanced SMA Crossover with ADX and RSI"
        )
        
        # Load parameters from config
        self.params = CONSERVATIVE_TREND_RIDER['parameters']
        self.filters = CONSERVATIVE_TREND_RIDER['filters']
        
        # Required data columns for this strategy
        self.required_columns = [
            'open', 'high', 'low', 'close', 'volume',
            f'SMA_{self.params["ema_fast"]}',  # 50 SMA
            f'SMA_{self.params["ema_slow"]}',  # 200 SMA
            f'ADX_{self.params["adx_threshold"]}',  # ADX_14 (not ADX_25)
            f'RSI_{self.params["rsi_length"]}'
        ]
        
        logger.info(f"Initialized {self.name} with parameters: {self.params}")
    
    def check_signal(self, symbol: str, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Check for conservative trend signals.
        
        Args:
            symbol (str): Trading pair symbol
            data (pd.DataFrame): Market data with indicators
            
        Returns:
            Optional[Dict[str, Any]]: Trading signal if conditions met
        """
        try:
            # Validate data
            if not self.validate_data(data, self.required_columns):
                return None
            
            # Get current and previous candles
            current = data.iloc[-1]
            previous = data.iloc[-2]
            
            # Check for bullish signal (Golden Cross)
            long_signal = self._check_golden_cross(current, previous, data)
            if long_signal:
                return long_signal
            
            # Check for bearish signal (Death Cross)
            short_signal = self._check_death_cross(current, previous, data)
            if short_signal:
                return short_signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking {self.name} signal: {e}")
            return None
    
    def _check_golden_cross(self, current: pd.Series, previous: pd.Series, 
                           data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Check for Golden Cross (bullish) signal conditions."""
        try:
            # 50 SMA crosses above 200 SMA
            golden_cross = (
                previous[f'SMA_{self.params["ema_fast"]}'] <= previous[f'SMA_{self.params["ema_slow"]}'] and
                current[f'SMA_{self.params["ema_fast"]}'] > current[f'SMA_{self.params["ema_slow"]}']
            )
            
            # ADX trend strength confirmation
            adx_strong = current[f'ADX_{self.params["adx_threshold"]}'] > self.params['adx_threshold']
            
            # RSI momentum validation
            rsi_bullish = current[f'RSI_{self.params["rsi_length"]}'] > self.params['rsi_upper']
            
            # Multiple timeframe confirmation (check if trend is consistent)
            trend_confirmed = self._check_trend_consistency(data, 'bullish')
            
            if golden_cross and adx_strong and rsi_bullish and trend_confirmed:
                # Calculate position size and stop loss
                stop_loss = current[f'SMA_{self.params["ema_slow"]}'] * 0.98  # 2% below 200 SMA
                take_profit = current['close'] * 1.05  # 5% take profit
                
                # Create signal
                signal = self.format_signal(
                    signal_type='long',
                    symbol=symbol,
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    leverage=self.params['leverage'],
                    trend_strength=current[f'ADX_{self.params["adx_threshold"]}']
                )
                
                logger.info(f"{self.name} GOLDEN CROSS signal triggered for {symbol}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking Golden Cross: {e}")
            return None
    
    def _check_death_cross(self, current: pd.Series, previous: pd.Series, 
                          data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Check for Death Cross (bearish) signal conditions."""
        try:
            # 50 SMA crosses below 200 SMA
            death_cross = (
                previous[f'SMA_{self.params["ema_fast"]}'] >= previous[f'SMA_{self.params["ema_slow"]}'] and
                current[f'SMA_{self.params["ema_fast"]}'] < current[f'SMA_{self.params["ema_slow"]}']
            )
            
            # ADX trend strength confirmation
            adx_strong = current[f'ADX_{self.params["adx_threshold"]}'] > self.params['adx_threshold']
            
            # RSI momentum validation
            rsi_bearish = current[f'RSI_{self.params["rsi_length"]}'] < self.params['rsi_lower']
            
            # Multiple timeframe confirmation (check if trend is consistent)
            trend_confirmed = self._check_trend_consistency(data, 'bearish')
            
            if death_cross and adx_strong and rsi_bearish and trend_confirmed:
                # Calculate position size and stop loss
                stop_loss = current[f'SMA_{self.params["ema_slow"]}'] * 1.02  # 2% above 200 SMA
                take_profit = current['close'] * 0.95  # 5% take profit
                
                # Create signal
                signal = self.format_signal(
                    signal_type='short',
                    symbol=symbol,
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    leverage=self.params['leverage'],
                    trend_strength=current[f'ADX_{self.params["adx_threshold"]}']
                )
                
                logger.info(f"{self.name} DEATH CROSS signal triggered for {symbol}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking Death Cross: {e}")
            return None
    
    def _check_trend_consistency(self, data: pd.DataFrame, direction: str) -> bool:
        """
        Check if trend is consistent across multiple timeframes.
        
        Args:
            data (pd.DataFrame): Market data
            direction (str): 'bullish' or 'bearish'
            
        Returns:
            bool: True if trend is consistent
        """
        try:
            if len(data) < 5:
                return False
            
            # Check last 5 candles for trend consistency
            recent_data = data.tail(5)
            
            if direction == 'bullish':
                # Check if 50 SMA is consistently above 200 SMA
                consistent = all(
                    recent_data[f'SMA_{self.params["ema_fast"]}'] > recent_data[f'SMA_{self.params["ema_slow"]}']
                )
            else:  # bearish
                # Check if 50 SMA is consistently below 200 SMA
                consistent = all(
                    recent_data[f'SMA_{self.params["ema_fast"]}'] < recent_data[f'SMA_{self.params["ema_slow"]}']
                )
            
            return consistent
            
        except Exception as e:
            logger.error(f"Error checking trend consistency: {e}")
            return False
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters."""
        return {
            'strategy_type': 'Conservative Trend Rider',
            'timeframe': self.timeframe,
            'parameters': self.params,
            'filters': self.filters,
            'required_columns': self.required_columns
        }
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """
        Update strategy parameters dynamically.
        
        Args:
            new_params (Dict[str, Any]): New parameters to update
        """
        try:
            # Update parameters
            if 'parameters' in new_params:
                self.params.update(new_params['parameters'])
            
            if 'filters' in new_params:
                self.filters.update(new_params['filters'])
            
            logger.info(f"Updated {self.name} parameters: {new_params}")
            
        except Exception as e:
            logger.error(f"Error updating {self.name} parameters: {e}")
