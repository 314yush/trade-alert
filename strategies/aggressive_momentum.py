"""
Aggressive Momentum Strategy

High-frequency scalping strategy using Stochastic RSI with volume confirmation.
This strategy can be modified independently without affecting other strategies.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import logging
from .base_strategy import BaseStrategy
from config import AGGRESSIVE_MOMENTUM_IGNITION

logger = logging.getLogger(__name__)


class AggressiveMomentumStrategy(BaseStrategy):
    """
    Aggressive Momentum Ignition Strategy (5-minute timeframe).
    
    High-frequency scalping strategy that looks for:
    - Stochastic RSI bullish/bearish crosses
    - Volume confirmation
    - Oversold/overbought conditions
    - RSI divergence (optional)
    """
    
    def __init__(self):
        """Initialize the aggressive momentum strategy."""
        super().__init__(
            name="Aggressive Momentum Ignition",
            timeframe="5m",
            description="Enhanced StochRSI with Volume Confirmation"
        )
        
        # Load parameters from config
        self.params = AGGRESSIVE_MOMENTUM_IGNITION['parameters']
        self.filters = AGGRESSIVE_MOMENTUM_IGNITION['filters']
        
        # Required data columns for this strategy
        self.required_columns = [
            'open', 'high', 'low', 'close', 'volume',
            f'STOCHRSIk_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}',
            f'STOCHRSId_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'
        ]
        
        logger.info(f"Initialized {self.name} with parameters: {self.params}")
    
    def check_signal(self, symbol: str, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Check for aggressive momentum signals.
        
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
            # StochRSI K crosses above D in oversold zone
            k_cross_above = (
                previous[f'STOCHRSIk_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] < 
                previous[f'STOCHRSId_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] and
                current[f'STOCHRSIk_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] > 
                current[f'STOCHRSId_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}']
            )
            
            # Both in oversold zone
            both_oversold = (
                previous[f'STOCHRSIk_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] < self.params['oversold_threshold'] and
                previous[f'STOCHRSId_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] < self.params['oversold_threshold']
            )
            
            # Volume confirmation
            volume_confirmed = self._check_volume_confirmation(data, self.params['volume_multiplier'])
            
            # Check for RSI divergence if enabled
            divergence_confirmed = True
            if self.filters.get('divergence_detection', False):
                divergence_confirmed = self._check_rsi_divergence(data, 'bullish', len(data) - 1)
            
            if k_cross_above and both_oversold and volume_confirmed and divergence_confirmed:
                # Calculate position size and stop loss
                stop_loss = current['close'] * 0.992  # 0.8% stop loss
                take_profit = current['close'] * 1.015  # 1.5% take profit
                
                # Create signal
                signal = self.format_signal(
                    signal_type='long',
                    symbol=symbol,
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    leverage=self.params['leverage'],
                    max_hold_period=self.params['max_hold_period'],
                    partial_exits=self.filters.get('partial_exits', [])
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
            # StochRSI K crosses below D in overbought zone
            k_cross_below = (
                previous[f'STOCHRSIk_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] > 
                previous[f'STOCHRSId_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] and
                current[f'STOCHRSIk_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] < 
                current[f'STOCHRSId_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}']
            )
            
            # Both in overbought zone
            both_overbought = (
                previous[f'STOCHRSIk_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] > self.params['overbought_threshold'] and
                previous[f'STOCHRSId_{self.params["stoch_rsi_k"]}_{self.params["stoch_rsi_d"]}_{self.params["rsi_length"]}'] > self.params['overbought_threshold']
            )
            
            # Volume confirmation
            volume_confirmed = self._check_volume_confirmation(data, self.params['volume_multiplier'])
            
            # Check for RSI divergence if enabled
            divergence_confirmed = True
            if self.filters.get('divergence_detection', False):
                divergence_confirmed = self._check_rsi_divergence(data, 'bearish', len(data) - 1)
            
            if k_cross_below and both_overbought and volume_confirmed and divergence_confirmed:
                # Calculate position size and stop loss
                stop_loss = current['close'] * 1.008  # 0.8% stop loss
                take_profit = current['close'] * 0.985  # 1.5% take profit
                
                # Create signal
                signal = self.format_signal(
                    signal_type='short',
                    symbol=symbol,
                    price=current['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    leverage=self.params['leverage'],
                    max_hold_period=self.params['max_hold_period'],
                    partial_exits=self.filters.get('partial_exits', [])
                )
                
                logger.info(f"{self.name} SHORT signal triggered for {symbol}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking bearish signal: {e}")
            return None
    
    def _check_volume_confirmation(self, data: pd.DataFrame, multiplier: float) -> bool:
        """Check if volume confirms the signal."""
        try:
            if len(data) < 20:
                return False
            
            # Calculate average volume
            avg_volume = data['volume'].tail(20).mean()
            current_volume = data['volume'].iloc[-1]
            
            return current_volume >= (avg_volume * multiplier)
            
        except Exception as e:
            logger.error(f"Error checking volume confirmation: {e}")
            return False
    
    def _check_rsi_divergence(self, data: pd.DataFrame, direction: str, index: int) -> bool:
        """Check for RSI divergence (placeholder implementation)."""
        # This is a placeholder - you can implement your own divergence logic
        try:
            # Simple divergence check (you can enhance this)
            if index < 10:
                return False
            
            # For now, just return True (no divergence check)
            # You can implement your own divergence detection logic here
            return True
            
        except Exception as e:
            logger.error(f"Error checking RSI divergence: {e}")
            return False
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters."""
        return {
            'strategy_type': 'Aggressive Momentum Ignition',
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
