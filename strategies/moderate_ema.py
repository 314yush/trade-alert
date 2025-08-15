"""
Moderate EMA Crossover Strategy

Swing trading strategy using EMA crossovers with RSI momentum confirmation.
This strategy can be modified independently without affecting other strategies.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import logging
from .base_strategy import BaseStrategy
from config import MODERATE_EMA_CROSSOVER

logger = logging.getLogger(__name__)


class ModerateEMAStrategy(BaseStrategy):
    """
    Moderate EMA Crossover Strategy (15-minute timeframe).
    
    Swing trading strategy that looks for:
    - Fast EMA crossing above/below slow EMA
    - RSI momentum confirmation
    - Higher timeframe trend validation
    - Volume spike confirmation
    """
    
    def __init__(self):
        """Initialize the moderate EMA strategy."""
        super().__init__(
            name="Moderate EMA Crossover",
            timeframe="15m",
            description="Enhanced EMA Crossover with RSI and Trend Filter"
        )
        
        # Load parameters from config
        self.params = MODERATE_EMA_CROSSOVER['parameters']
        self.filters = MODERATE_EMA_CROSSOVER['filters']
        
        # Required data columns for this strategy
        self.required_columns = [
            'open', 'high', 'low', 'close', 'volume',
            f'EMA_{self.params["ema_fast"]}',
            f'EMA_{self.params["ema_slow"]}',
            f'RSI_{self.params["rsi_length"]}',
            f'EMA_{self.params["trend_ema"]}'  # Trend filter
        ]
        
        logger.info(f"Initialized {self.name} with parameters: {self.params}")
    
    def check_signal(self, symbol: str, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Check for moderate EMA crossover signals.
        
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
            
            # Check for bullish signal
            long_signal = self._check_bullish_signal(current, previous, data)
            if long_signal:
                return long_signal
            
            # Check for bearish signal
            short_signal = self._check_bearish_signal(current, previous, data)
            if short_signal:
                return short_signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking {self.name} signal: {e}")
            return None
    
    def _check_bullish_signal(self, current: pd.Series, previous: pd.Series, 
                             data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Check for bullish (long) signal conditions."""
        try:
            # Fast EMA crosses above slow EMA
            ema_cross_above = (
                previous[f'EMA_{self.params["ema_fast"]}'] <= previous[f'EMA_{self.params["ema_slow"]}'] and
                current[f'EMA_{self.params["ema_fast"]}'] > current[f'EMA_{self.params["ema_slow"]}']
            )
            
            # RSI momentum confirmation
            rsi_bullish = current[f'RSI_{self.params["rsi_length"]}'] > self.params['rsi_bullish']
            
            # Trend confirmation (higher timeframe)
            trend_bullish = current[f'EMA_{self.params["trend_ema"]}'] < current['close']
            
            # Volume confirmation
            volume_confirmed = self._check_volume_spike(data, self.filters.get('required_volume_spike', 1.8))
            
            # Candle body confirmation
            candle_confirmed = self._check_candle_body(current, self.filters.get('min_candle_body', 0.005))
            
            if (ema_cross_above and rsi_bullish and trend_bullish and 
                volume_confirmed and candle_confirmed):
                
                # Calculate position size and stop loss
                stop_loss = current['close'] * 0.985  # 1.5% stop loss
                take_profit = current['close'] * 1.0375  # 2.5x risk-reward
                
                # Create signal
                signal = self.format_signal(
                    signal_type='long',
                    symbol=symbol,
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    leverage=self.params['leverage'],
                    position_size=self.params['position_size']
                )
                
                logger.info(f"{self.name} LONG signal triggered for {symbol}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking bullish signal: {e}")
            return None
    
    def _check_bearish_signal(self, current: pd.Series, previous: pd.Series, 
                             data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Check for bearish (short) signal conditions."""
        try:
            # Fast EMA crosses below slow EMA
            ema_cross_below = (
                previous[f'EMA_{self.params["ema_fast"]}'] >= previous[f'EMA_{self.params["ema_slow"]}'] and
                current[f'EMA_{self.params["ema_fast"]}'] < current[f'EMA_{self.params["ema_slow"]}']
            )
            
            # RSI momentum confirmation
            rsi_bearish = current[f'RSI_{self.params["rsi_length"]}'] < self.params['rsi_bearish']
            
            # Trend confirmation (higher timeframe)
            trend_bearish = current[f'EMA_{self.params["trend_ema"]}'] > current['close']
            
            # Volume confirmation
            volume_confirmed = self._check_volume_spike(data, self.filters.get('required_volume_spike', 1.8))
            
            # Candle body confirmation
            candle_confirmed = self._check_candle_body(current, self.filters.get('min_candle_body', 0.005))
            
            if (ema_cross_below and rsi_bearish and trend_bearish and 
                volume_confirmed and candle_confirmed):
                
                # Calculate position size and stop loss
                stop_loss = current['close'] * 1.015  # 1.5% stop loss
                take_profit = current['close'] * 0.9625  # 2.5x risk-reward
                
                # Create signal
                signal = self.format_signal(
                    signal_type='short',
                    symbol=symbol,
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    leverage=self.params['leverage'],
                    position_size=self.params['position_size']
                )
                
                logger.info(f"{self.name} SHORT signal triggered for {symbol}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking bearish signal: {e}")
            return None
    
    def _check_volume_spike(self, data: pd.DataFrame, multiplier: float) -> bool:
        """Check if volume spike confirms the signal."""
        try:
            if len(data) < 20:
                return False
            
            # Calculate average volume
            avg_volume = data['volume'].tail(20).mean()
            current_volume = data['volume'].iloc[-1]
            
            return current_volume >= (avg_volume * multiplier)
            
        except Exception as e:
            logger.error(f"Error checking volume spike: {e}")
            return False
    
    def _check_candle_body(self, candle: pd.Series, min_body: float) -> bool:
        """Check if candle body meets minimum requirement."""
        try:
            body_size = abs(candle['close'] - candle['open']) / candle['open']
            return body_size >= min_body
            
        except Exception as e:
            logger.error(f"Error checking candle body: {e}")
            return False
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters."""
        return {
            'strategy_type': 'Moderate EMA Crossover',
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
