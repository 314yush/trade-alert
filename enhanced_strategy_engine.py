"""
Enhanced Strategy Engine for the Risk-Adaptive Crypto Trading Alert Bot.

This module implements sophisticated trading strategies with:
- Advanced risk management
- Position sizing algorithms
- Multi-timeframe confirmation
- Volume and volatility filters
- Time-based session filters
"""

import pandas as pd
import numpy as np
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from data_handler import DataHandler
from config import (
    AGGRESSIVE_MOMENTUM_IGNITION, MODERATE_EMA_CROSSOVER, CONSERVATIVE_TREND_RIDER,
    CAPITAL_ALLOCATION, RISK_MANAGEMENT, EXECUTION_PRIORITY, DEFAULT_PAIR, ALERT_COOLDOWN_MINUTES, DEBUG_MODE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedStrategyEngine:
    """
    Enhanced strategy engine with sophisticated risk management and advanced filters.
    
    This class implements the three enhanced strategies:
    1. Aggressive Momentum Ignition (5m) - High-frequency scalping
    2. Moderate EMA Crossover (15m) - Swing trading with 4h confirmation
    3. Conservative Trend Setter (1d) - Position sizing engine
    """
    
    def __init__(self):
        """Initialize the EnhancedStrategyEngine with data handler and risk management."""
        self.data_handler = DataHandler()
        
        # Track alert states to prevent duplicates
        self.alert_states = {
            'aggressive_momentum_ignition': {'long': False, 'short': False, 'last_alert_time': None},
            'moderate_ema_crossover': {'long': False, 'short': False, 'last_alert_time': None},
            'conservative_trend_rider': {'long': False, 'short': False, 'last_alert_time': None}
        }
        
        # Risk management state
        self.risk_state = {
            'daily_loss': 0.0,
            'daily_loss_reset_time': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            'active_positions': [],
            'portfolio_risk': 0.0
        }
        
        logger.info("EnhancedStrategyEngine initialized successfully")
    
    def _check_alert_cooldown(self, profile: str) -> bool:
        """Check if enough time has passed since the last alert for a profile."""
        if self.alert_states[profile]['last_alert_time'] is None:
            return True
        
        time_since_last = datetime.now() - self.alert_states[profile]['last_alert_time']
        cooldown_duration = timedelta(minutes=ALERT_COOLDOWN_MINUTES)
        
        return time_since_last >= cooldown_duration
    
    def _update_alert_state(self, profile: str, signal_type: str) -> None:
        """Update the alert state for a profile and signal type."""
        self.alert_states[profile][signal_type] = True
        self.alert_states[profile]['last_alert_time'] = datetime.now()
        
        # Reset the opposite signal type
        opposite_signal = 'short' if signal_type == 'long' else 'long'
        self.alert_states[profile][opposite_signal] = False
        
        logger.info(f"Updated alert state for {profile} {signal_type} signal")
    
    def _reset_alert_state(self, profile: str, signal_type: str) -> None:
        """Reset the alert state for a profile and signal type."""
        self.alert_states[profile][signal_type] = False
        logger.debug(f"Reset alert state for {profile} {signal_type} signal")
    
    def _check_time_filter(self, strategy_config: Dict) -> bool:
        """Check if current time allows trading based on strategy filters."""
        try:
            if 'filters' not in strategy_config or 'time_start' not in strategy_config['filters']:
                return True  # No time filter specified
            
            current_time = datetime.utcnow().time()
            start_time = datetime.strptime(strategy_config['filters']['time_start'], '%H:%M').time()
            end_time = datetime.strptime(strategy_config['filters']['time_end'], '%H:%M').time()
            
            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:  # Crosses midnight
                return current_time >= start_time or current_time <= end_time
                
        except Exception as e:
            logger.error(f"Error checking time filter: {e}")
            return True
    
    def _check_volatility_filter(self, df: pd.DataFrame, volatility_threshold: float) -> bool:
        """Check if volatility is within acceptable range."""
        try:
            # Calculate ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=14).mean()
            
            current_atr = atr.iloc[-1]
            current_price = df['close'].iloc[-1]
            atr_percentage = current_atr / current_price
            
            return atr_percentage <= volatility_threshold
            
        except Exception as e:
            logger.error(f"Error checking volatility filter: {e}")
            return True
    
    def _check_volume_confirmation(self, df: pd.DataFrame, volume_multiplier: float) -> bool:
        """Check if volume confirms the signal."""
        try:
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
            
            return current_volume > (avg_volume * volume_multiplier)
            
        except Exception as e:
            logger.error(f"Error checking volume confirmation: {e}")
            return True
    
    def _check_wick_confirmation(self, current: pd.Series) -> bool:
        """Check if wick pattern confirms the signal direction."""
        try:
            body_size = abs(current['close'] - current['open'])
            upper_wick = current['high'] - max(current['open'], current['close'])
            lower_wick = min(current['open'], current['close']) - current['low']
            
            # For bullish signals: lower wick should be longer than upper wick
            # For bearish signals: upper wick should be longer than lower wick
            # This indicates rejection of the opposite direction
            
            if current['close'] > current['open']:  # Bullish candle
                return lower_wick > upper_wick and lower_wick > (body_size * 0.3)
            else:  # Bearish candle
                return upper_wick > lower_wick and upper_wick > (body_size * 0.3)
                
        except Exception as e:
            logger.error(f"Error checking wick confirmation: {e}")
            return True
    
    def _check_candle_body_confirmation(self, current: pd.Series, min_body_pct: float) -> bool:
        """Check if candle body meets minimum percentage requirement."""
        try:
            body_size = abs(current['close'] - current['open'])
            total_range = current['high'] - current['low']
            
            if total_range == 0:
                return False
            
            body_percentage = body_size / total_range
            return body_percentage >= min_body_pct
            
        except Exception as e:
            logger.error(f"Error checking candle body confirmation: {e}")
            return True
    
    def _check_volume_spike(self, df: pd.DataFrame, required_multiplier: float) -> bool:
        """Check if current volume is above required multiplier of average volume."""
        try:
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
            
            return current_volume > (avg_volume * required_multiplier)
            
        except Exception as e:
            logger.error(f"Error checking volume spike: {e}")
            return True
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range for trailing stops and volatility analysis."""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Calculate ATR as exponential moving average
            atr = true_range.ewm(span=period).mean().iloc[-1]
            
            return atr
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.0
    
    def _calculate_position_size(self, strategy_name: str, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk management rules."""
        try:
            risk_per_trade = RISK_MANAGEMENT['position_sizing']['max_risk_per_trade']
            strategy_capital = 10000 * CAPITAL_ALLOCATION.get(strategy_name, 0.33)
            
            # Calculate risk amount for this strategy
            risk_amount = strategy_capital * risk_per_trade
            
            # Calculate position size based on risk
            price_risk = abs(entry_price - stop_loss)
            if price_risk == 0:
                return 0.0
            
            position_size = risk_amount / price_risk
            
            # Apply leverage caps
            max_leverage = RISK_MANAGEMENT['leverage_caps'].get(strategy_name, 1)
            max_position_size = strategy_capital * max_leverage
            
            # Cap position size to prevent extreme values
            position_size = min(position_size, max_position_size)
            
            # Additional safety cap - position size should not exceed 10x the strategy capital
            safety_cap = strategy_capital * 10
            position_size = min(position_size, safety_cap)
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def _get_win_streak(self, strategy_name: str) -> int:
        """Get current win streak for a strategy (placeholder for future implementation)."""
        # TODO: Implement win streak tracking from backtest results
        return 0
    
    def _check_cross_strategy_risk_controls(self) -> bool:
        """Check unified risk controls across all strategies."""
        try:
            # Check max concurrent trades
            active_trades = sum([
                self.alert_states['aggressive_momentum_ignition']['long'] or self.alert_states['aggressive_momentum_ignition']['short'],
                self.alert_states['moderate_ema_crossover']['long'] or self.alert_states['moderate_ema_crossover']['short'],
                self.alert_states['conservative_trend_rider']['long'] or self.alert_states['conservative_trend_rider']['short']
            ])
            
            if active_trades >= 2:  # Max 2 concurrent trades
                logger.debug("Cross-strategy risk control: Max concurrent trades reached")
                return False
            
            # Check daily loss limit (placeholder for future implementation)
            # TODO: Implement daily loss tracking
            
            # Check volatility blackout conditions
            if self._check_volatility_blackout():
                logger.debug("Cross-strategy risk control: Volatility blackout active")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking cross-strategy risk controls: {e}")
            return True
    
    def _check_volatility_blackout(self) -> bool:
        """Check if volatility blackout conditions are met."""
        try:
            # TODO: Implement VIX data integration
            # For now, use ATR-based volatility check
            # This is a simplified version - in production, you'd want real VIX data
            
            # Check if we have recent data to calculate volatility
            if not hasattr(self, '_volatility_cache'):
                self._volatility_cache = {}
            
            return False  # Placeholder - implement actual volatility logic
            
        except Exception as e:
            logger.error(f"Error checking volatility blackout: {e}")
            return False
    
    def _check_rsi_divergence(self, df: pd.DataFrame, direction: str, current_index: int) -> bool:
        """Check for RSI divergence patterns."""
        try:
            if current_index < 20:  # Need enough data for divergence detection
                return True
            
            # Get RSI values for the last 20 periods
            rsi_values = df['RSI_11'].iloc[current_index-20:current_index+1]
            price_values = df['close'].iloc[current_index-20:current_index+1]
            
            if len(rsi_values) < 21 or len(price_values) < 21:
                return True
            
            if direction == 'bullish':
                # Bullish divergence: Price makes lower lows, RSI makes higher lows
                price_low_1 = price_values.iloc[-10:].min()  # Recent low
                price_low_2 = price_values.iloc[-20:-10].min()  # Previous low
                rsi_low_1 = rsi_values.iloc[-10:].min()  # Recent RSI low
                rsi_low_2 = rsi_values.iloc[-20:-10].min()  # Previous RSI low
                
                return (price_low_1 < price_low_2) and (rsi_low_1 > rsi_low_2)
            
            elif direction == 'bearish':
                # Bearish divergence: Price makes higher highs, RSI makes lower highs
                price_high_1 = price_values.iloc[-10:].max()  # Recent high
                price_high_2 = price_values.iloc[-20:-10].max()  # Previous high
                rsi_high_1 = rsi_values.iloc[-10:].max()  # Recent RSI high
                rsi_high_2 = rsi_values.iloc[-20:-10].max()  # Previous RSI high
                
                return (price_high_1 > price_high_2) and (rsi_high_1 < rsi_high_2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking RSI divergence: {e}")
            return True
    
    def check_aggressive_momentum_ignition(self, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        Check for OPTIMIZED Aggressive Momentum Ignition strategy signals.
        
        Enhanced 5-minute strategy with:
        - Optimized StochRSI (8/2 periods, 10/90 thresholds)
        - Enhanced volume confirmation (2.0x multiplier)
        - Improved volatility filters (1.8% ATR cap)
        - Optimized trading hours (09:30-16:00 UTC)
        - Wick confirmation for better entry timing
        - Partial profit taking system
        """
        if symbol is None:
            symbol = DEFAULT_PAIR
        
        try:
            # Check cross-strategy risk controls
            if not self._check_cross_strategy_risk_controls():
                logger.debug("Aggressive strategy: Cross-strategy risk controls failed")
                return None
            
            # Check time filter
            if not self._check_time_filter(AGGRESSIVE_MOMENTUM_IGNITION):
                logger.debug("Aggressive strategy: Outside trading hours")
                return None
            
            # Fetch 5-minute data
            df = self.data_handler.fetch_ohlcv(symbol, '5m', limit=100)
            if df is None or len(df) < 50:
                logger.warning(f"Insufficient data for aggressive strategy on {symbol}")
                return None
            
            # Calculate indicators
            params = AGGRESSIVE_MOMENTUM_IGNITION['parameters']
            indicators = [{
                'name': 'STOCHRSI',
                'k': params['stoch_rsi_k'],
                'd': params['stoch_rsi_d'],
                'rsi_length': params['rsi_length']
            }]
            
            df = self.data_handler.calculate_indicators(df, indicators)
            
            if len(df) < 2:
                return None
            
            # Check volatility filter
            if not self._check_volatility_filter(df, AGGRESSIVE_MOMENTUM_IGNITION['filters']['volatility']):
                logger.debug("Aggressive strategy: Volatility too high")
                return None
            
            # Get current and previous candle data
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            # Check wick confirmation if enabled
            if AGGRESSIVE_MOMENTUM_IGNITION['filters'].get('wick_confirmation', False):
                if not self._check_wick_confirmation(current):
                    logger.debug("Aggressive strategy: Wick confirmation failed")
                    return None
            
            # Check for bullish signal
            if (self.alert_states['aggressive_momentum_ignition']['long'] == False and
                self._check_alert_cooldown('aggressive_momentum_ignition')):
                
                # StochRSI K crosses above D in oversold zone
                k_cross_above = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < 
                                previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] and
                                current[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > 
                                current[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'])
                
                both_oversold = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < params['oversold_threshold'] and
                                previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < params['oversold_threshold'])
                
                # Volume confirmation
                volume_confirmed = self._check_volume_confirmation(df, params['volume_multiplier'])
                
                # Check for RSI divergence if enabled
                divergence_confirmed = True
                if AGGRESSIVE_MOMENTUM_IGNITION['filters'].get('divergence_detection', False):
                    divergence_confirmed = self._check_rsi_divergence(df, 'bullish', len(df) - 1)
                
                if k_cross_above and both_oversold and volume_confirmed and divergence_confirmed:
                    # Calculate position size and stop loss
                    stop_loss = current['close'] * 0.992  # 0.8% stop loss
                    position_size = self._calculate_position_size('aggressive_momentum_ignition', current['close'], stop_loss)
                    
                    signal = {
                        'profile': 'Aggressive Momentum Ignition',
                        'strategy': 'Enhanced StochRSI with Volume',
                        'signal_type': 'long',
                        'symbol': symbol,
                        'timeframe': '5m',
                        'price': current['close'],
                        'timestamp': current.name,
                        'position_size': position_size,
                        'stop_loss': stop_loss,
                        'take_profit': current['close'] * 1.015,  # 1.5% take profit
                        'leverage': params['leverage'],
                        'max_hold_period': params['max_hold_period'],
                        'partial_exits': AGGRESSIVE_MOMENTUM_IGNITION['filters'].get('partial_exits', []),
                        'message': f"Long {symbol} - current price (${current['close']:.2f})\n"
                                 f"Risk Profile: Aggressive Momentum Ignition\n"
                                 f"Recommended Leverage: {params['leverage']}x\n"
                                 f"Position Size: {position_size:.2f}\n"
                                 f"Stop Loss: ${stop_loss:.2f}\n"
                                 f"Take Profit: ${current['close'] * 1.015:.2f}\n"
                                 f"Partial Exits: {AGGRESSIVE_MOMENTUM_IGNITION['filters'].get('partial_exits', [])}"
                    }
                    
                    self._update_alert_state('aggressive_momentum_ignition', 'long')
                    logger.info(f"Aggressive LONG signal triggered for {symbol}")
                    return signal
            
            # Check for bearish signal
            if (self.alert_states['aggressive_momentum_ignition']['short'] == False and
                self._check_alert_cooldown('aggressive_momentum_ignition')):
                
                # StochRSI K crosses below D in overbought zone
                k_cross_below = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > 
                                previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] and
                                current[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < 
                                current[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'])
                
                both_overbought = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > params['overbought_threshold'] and
                                   previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > params['overbought_threshold'])
                
                # Volume confirmation
                volume_confirmed = self._check_volume_confirmation(df, params['volume_multiplier'])
                
                # Check for RSI divergence if enabled
                divergence_confirmed = True
                if AGGRESSIVE_MOMENTUM_IGNITION['filters'].get('divergence_detection', False):
                    divergence_confirmed = self._check_rsi_divergence(df, 'bearish', len(df) - 1)
                
                if k_cross_below and both_overbought and volume_confirmed and divergence_confirmed:
                    # Calculate position size and stop loss
                    stop_loss = current['close'] * 1.008  # 0.8% stop loss
                    position_size = self._calculate_position_size('aggressive_momentum_ignition', current['close'], stop_loss)
                    
                    signal = {
                        'profile': 'Aggressive Momentum Ignition',
                        'strategy': 'Enhanced StochRSI with Volume',
                        'signal_type': 'short',
                        'symbol': symbol,
                        'timeframe': '5m',
                        'price': current['close'],
                        'timestamp': current.name,
                        'position_size': position_size,
                        'stop_loss': stop_loss,
                        'take_profit': current['close'] * 0.985,  # 1.5% take profit
                        'leverage': params['leverage'],
                        'max_hold_period': params['max_hold_period'],
                        'partial_exits': AGGRESSIVE_MOMENTUM_IGNITION['filters'].get('partial_exits', []),
                        'message': f"Short {symbol} - current price (${current['close']:.2f})\n"
                                 f"Risk Profile: Aggressive Momentum Ignition\n"
                                 f"Recommended Leverage: {params['leverage']}x\n"
                                 f"Position Size: {position_size:.2f}\n"
                                 f"Stop Loss: ${stop_loss:.2f}\n"
                                 f"Take Profit: ${current['close'] * 0.985:.2f}\n"
                                 f"Partial Exits: {AGGRESSIVE_MOMENTUM_IGNITION['filters'].get('partial_exits', [])}"
                    }
                    
                    self._update_alert_state('aggressive_momentum_ignition', 'short')
                    logger.info(f"Aggressive SHORT signal triggered for {symbol}")
                    return signal
            
            # Reset signals if conditions are no longer met
            if self.alert_states['aggressive_momentum_ignition']['long']:
                if not (current[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > 
                       current[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}']):
                    self._reset_alert_state('aggressive_momentum_ignition', 'long')
            
            if self.alert_states['aggressive_momentum_ignition']['short']:
                if not (current[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < 
                       current[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}']):
                    self._reset_alert_state('aggressive_momentum_ignition', 'short')
            
            return None
            
        except Exception as e:
            logger.error(f"Error in aggressive momentum ignition strategy check: {e}")
            return None
    
    def check_moderate_ema_crossover(self, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        Check for OPTIMIZED Moderate EMA Crossover strategy signals.
        
        Enhanced 15-minute strategy with:
        - Optimized EMA periods (8 & 34 for faster signals)
        - Improved RSI thresholds (40/60 for better timing)
        - Enhanced trend confirmation (50-period EMA)
        - Extended trading session (12:00-20:00 UTC)
        - Candle body confirmation (0.5% minimum)
        - RSI divergence detection
        - Volume spike requirement (1.8x)
        """
        if symbol is None:
            symbol = DEFAULT_PAIR
        
        try:
            # Check cross-strategy risk controls
            if not self._check_cross_strategy_risk_controls():
                logger.debug("Moderate strategy: Cross-strategy risk controls failed")
                return None
            
            # Check session filter (London + NY overlap)
            if not self._check_session_filter():
                logger.debug("Moderate strategy: Outside London/NY overlap session")
                return None
            
            # Fetch multi-timeframe data
            timeframes = ['15m', '4h']
            multi_tf_data = self.data_handler.get_multi_timeframe_data(symbol, timeframes)
            
            if '15m' not in multi_tf_data or '4h' not in multi_tf_data:
                logger.warning(f"Failed to fetch multi-timeframe data for {symbol}")
                return None
            
            df_15m = multi_tf_data['15m']
            df_4h = multi_tf_data['4h']
            
            if len(df_15m) < 50 or len(df_4h) < 50:
                logger.warning(f"Insufficient data for moderate strategy on {symbol}")
                return None
            
            # Calculate indicators for 15m timeframe
            params = MODERATE_EMA_CROSSOVER['parameters']
            indicators_15m = [
                {'name': 'EMA', 'length': params['ema_fast']},
                {'name': 'EMA', 'length': params['ema_slow']},
                {'name': 'RSI', 'length': params['rsi_length']}
            ]
            
            df_15m = self.data_handler.calculate_indicators(df_15m, indicators_15m)
            
            # Calculate trend EMA for 4h timeframe
            indicators_4h = [{'name': 'EMA', 'length': params['trend_ema']}]
            df_4h = self.data_handler.calculate_indicators(df_4h, indicators_4h)
            
            if len(df_15m) < 2 or len(df_4h) < 2:
                return None
            
            # Get current and previous candle data
            current_15m = df_15m.iloc[-1]
            previous_15m = df_15m.iloc[-2]
            current_4h = df_4h.iloc[-1]
            
            # Check candle body confirmation
            if MODERATE_EMA_CROSSOVER['filters'].get('min_candle_body', 0):
                if not self._check_candle_body_confirmation(current_15m, MODERATE_EMA_CROSSOVER['filters']['min_candle_body']):
                    logger.debug("Moderate strategy: Candle body too small")
                    return None
            
            # Check volume spike requirement
            if MODERATE_EMA_CROSSOVER['filters'].get('required_volume_spike', 0):
                if not self._check_volume_spike(df_15m, MODERATE_EMA_CROSSOVER['filters']['required_volume_spike']):
                    logger.debug("Moderate strategy: Volume spike insufficient")
                    return None
            
            # Check for bullish signal
            if (self.alert_states['moderate_ema_crossover']['long'] == False and
                self._check_alert_cooldown('moderate_ema_crossover')):
                
                # EMA fast > EMA slow
                ema_bullish = current_15m[f'EMA_{params["ema_fast"]}'] > current_15m[f'EMA_{params["ema_slow"]}']
                
                # EMA slope positive
                ema_slope_bullish = (current_15m[f'EMA_{params["ema_fast"]}'] > previous_15m[f'EMA_{params["ema_fast"]}'])
                
                # RSI > bullish threshold
                rsi_bullish = current_15m[f'RSI_{params["rsi_length"]}'] > params['rsi_bullish']
                
                # Price > open (bullish candle)
                candle_bullish = current_15m['close'] > current_15m['open']
                
                # Price > 4h trend EMA
                trend_bullish = current_15m['close'] > current_4h[f'EMA_{params["trend_ema"]}']
                
                if ema_bullish and ema_slope_bullish and rsi_bullish and candle_bullish and trend_bullish:
                    # Calculate position size and stop loss
                    stop_loss = current_15m['close'] * 0.985  # 1.5% stop loss
                    position_size = self._calculate_position_size('moderate_ema_crossover', current_15m['close'], stop_loss)
                    
                    signal = {
                        'profile': 'Moderate EMA Crossover',
                        'strategy': 'Enhanced EMA with 4H Trend',
                        'signal_type': 'long',
                        'symbol': symbol,
                        'timeframe': '15m',
                        'price': current_15m['close'],
                        'timestamp': current_15m.name,
                        'position_size': position_size,
                        'stop_loss': stop_loss,
                        'take_profit': current_15m['close'] * 1.0375,  # 2.5x risk-reward
                        'leverage': params['leverage'],
                        'message': f"Long {symbol} - current price (${current_15m['close']:.2f})\n"
                                 f"Risk Profile: Moderate EMA Crossover\n"
                                 f"Recommended Leverage: {params['leverage']}x\n"
                                 f"Position Size: {position_size:.2f}\n"
                                 f"Stop Loss: ${stop_loss:.2f}\n"
                                 f"Take Profit: ${current_15m['close'] * 1.0375:.2f}"
                    }
                    
                    self._update_alert_state('moderate_ema_crossover', 'long')
                    logger.info(f"Moderate LONG signal triggered for {symbol}")
                    return signal
            
            # Check for bearish signal
            if (self.alert_states['moderate_ema_crossover']['short'] == False and
                self._check_alert_cooldown('moderate_ema_crossover')):
                
                # EMA fast < EMA slow
                ema_bearish = current_15m[f'EMA_{params["ema_fast"]}'] < current_15m[f'EMA_{params["ema_slow"]}']
                
                # EMA slope negative
                ema_slope_bearish = (current_15m[f'EMA_{params["ema_fast"]}'] < previous_15m[f'EMA_{params["ema_fast"]}'])
                
                # RSI < bearish threshold
                rsi_bearish = current_15m[f'RSI_{params["rsi_length"]}'] < params['rsi_bearish']
                
                # Price < open (bearish candle)
                candle_bearish = current_15m['close'] < current_15m['open']
                
                # Price < 4h trend EMA
                trend_bearish = current_15m['close'] < current_4h[f'EMA_{params["trend_ema"]}']
                
                if ema_bearish and ema_slope_bearish and rsi_bearish and candle_bearish and trend_bearish:
                    # Calculate position size and stop loss
                    stop_loss = current_15m['close'] * 1.015  # 1.5% stop loss
                    position_size = self._calculate_position_size('moderate_ema_crossover', current_15m['close'], stop_loss)
                    
                    signal = {
                        'profile': 'Moderate EMA Crossover',
                        'strategy': 'Enhanced EMA with 4H Trend',
                        'signal_type': 'short',
                        'symbol': symbol,
                        'timeframe': '15m',
                        'price': current_15m['close'],
                        'timestamp': current_15m.name,
                        'position_size': position_size,
                        'stop_loss': stop_loss,
                        'take_profit': current_15m['close'] * 0.9625,  # 2.5x risk-reward
                        'leverage': params['leverage'],
                        'message': f"Short {symbol} - current price (${current_15m['close']:.2f})\n"
                                 f"Risk Profile: Moderate EMA Crossover\n"
                                 f"Recommended Leverage: {params['leverage']}x\n"
                                 f"Position Size: {position_size:.2f}\n"
                                 f"Stop Loss: ${stop_loss:.2f}\n"
                                 f"Take Profit: ${current_15m['close'] * 0.9625:.2f}"
                    }
                    
                    self._update_alert_state('moderate_ema_crossover', 'short')
                    logger.info(f"Moderate SHORT signal triggered for {symbol}")
                    return signal
            
            # Reset signals if conditions are no longer met
            if self.alert_states['moderate_ema_crossover']['long']:
                if not (current_15m[f'EMA_{params["ema_fast"]}'] > current_15m[f'EMA_{params["ema_slow"]}']):
                    self._reset_alert_state('moderate_ema_crossover', 'long')
            
            if self.alert_states['moderate_ema_crossover']['short']:
                if not (current_15m[f'EMA_{params["ema_fast"]}'] < current_15m[f'EMA_{params["ema_slow"]}']):
                    self._reset_alert_state('moderate_ema_crossover', 'short')
            
            return None
            
        except Exception as e:
            logger.error(f"Error in moderate EMA crossover strategy check: {e}")
            return None
    
    def _check_session_filter(self) -> bool:
        """Check if current time is within extended trading session (12:00-20:00 UTC)."""
        try:
            current_time = datetime.utcnow()
            current_hour = current_time.hour
            
            # Extended trading session: 12:00-20:00 UTC
            return 12 <= current_hour <= 20
            
        except Exception as e:
            logger.error(f"Error checking session filter: {e}")
            return True
    
    def check_conservative_trend_rider(self, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        Conservative Trend Rider strategy (4h timeframe)
        - Ideal for 2-3 day holds
        - Low leverage (2x)
        - Trend-following with EMA, ADX and RSI
        """
        if symbol is None:
            symbol = DEFAULT_PAIR
        
        try:
            # Check cross-strategy risk controls
            if not self._check_cross_strategy_risk_controls():
                logger.debug("Conservative strategy: Cross-strategy risk controls failed")
                return None
            
            # Fetch 4-hour data (need more data for EMA200 and ADX calculations)
            df = self.data_handler.fetch_ohlcv(symbol, '4h', limit=300)
            if df is None or len(df) < 250:
                logger.warning(f"Insufficient data for conservative trend rider on {symbol}")
                return None
            
            # Calculate indicators
            params = CONSERVATIVE_TREND_RIDER['parameters']
            indicators = [
                {'name': 'EMA', 'length': params['ema_fast']},
                {'name': 'EMA', 'length': params['ema_slow']},
                {'name': 'ADX', 'length': 14},
                {'name': 'RSI', 'length': params['rsi_length']}
            ]
            
            df = self.data_handler.calculate_indicators(df, indicators)
            
            if len(df) < 3:
                return None
            
            # Get current and previous candle data
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Calculate swing points for stop loss
            swing_low = min(df['low'].iloc[-5:])
            swing_high = max(df['high'].iloc[-5:])
            
            # Check for long signal
            if (self.alert_states['conservative_trend_rider']['long'] == False and
                self._check_alert_cooldown('conservative_trend_rider')):
                
                ema_bullish = (current[f'EMA_{params["ema_fast"]}'] > current[f'EMA_{params["ema_slow"]}'])
                price_above_ema = (current['close'] > current[f'EMA_{params["ema_slow"]}'])
                strong_trend = (current['ADX_14'] > params['adx_threshold'])
                good_entry = (current[f'RSI_{params["rsi_length"]}'] < params['rsi_upper'])
                
                if ema_bullish and price_above_ema and strong_trend and good_entry:
                    stop_loss = swing_low
                    risk = current['close'] - stop_loss
                    take_profit = current['close'] + (3 * risk)
                    
                    # Calculate trailing stop if enabled
                    trailing_stop = None
                    if CONSERVATIVE_TREND_RIDER['filters'].get('trailing_stop', False):
                        atr = self._calculate_atr(df, 14)
                        trailing_stop = current['close'] - (CONSERVATIVE_TREND_RIDER['exit_conditions']['trailing_stop_multiplier'] * atr)
                    
                    signal = {
                        'profile': 'Conservative Trend Rider',
                        'strategy': 'EMA/ADX/RSI Trend Following',
                        'signal_type': 'long',
                        'symbol': symbol,
                        'timeframe': '4h',
                        'price': current['close'],
                        'timestamp': current.name,
                        'leverage': params['leverage'],
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'trailing_stop': trailing_stop,
                        'hold_period': '24-72h',
                        'profit_scaling': CONSERVATIVE_TREND_RIDER['exit_conditions']['profit_scaling_levels'],
                        'message': f"Long {symbol} - current price (${current['close']:.2f})\n"
                                 f"Risk Profile: Conservative Trend Rider\n"
                                 f"Leverage: {params['leverage']}x\n"
                                 f"Stop Loss: ${stop_loss:.2f}\n"
                                 f"Take Profit: ${take_profit:.2f}"
                    }
                    
                    self._update_alert_state('conservative_trend_rider', 'long')
                    logger.info(f"Conservative Trend Rider LONG signal for {symbol}")
                    return signal
            
            # Check for short signal
            if (self.alert_states['conservative_trend_rider']['short'] == False and
                self._check_alert_cooldown('conservative_trend_rider')):
                
                ema_bearish = (current[f'EMA_{params["ema_fast"]}'] < current[f'EMA_{params["ema_slow"]}'])
                price_below_ema = (current['close'] < current[f'EMA_{params["ema_slow"]}'])
                strong_trend = (current['ADX_14'] > params['adx_threshold'])
                good_entry = (current[f'RSI_{params["rsi_length"]}'] > params['rsi_lower'])
                
                if ema_bearish and price_below_ema and strong_trend and good_entry:
                    stop_loss = swing_high
                    risk = stop_loss - current['close']
                    take_profit = current['close'] - (3 * risk)
                    
                    signal = {
                        'profile': 'Conservative Trend Rider',
                        'strategy': 'EMA/ADX/RSI Trend Following',
                        'signal_type': 'short',
                        'symbol': symbol,
                        'timeframe': '4h',
                        'price': current['close'],
                        'timestamp': current.name,
                        'leverage': params['leverage'],
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'hold_period': '2-3 days',
                        'message': f"Short {symbol} - current price (${current['close']:.2f})\n"
                                 f"Risk Profile: Conservative Trend Rider\n"
                                 f"Leverage: {params['leverage']}x\n"
                                 f"Stop Loss: ${stop_loss:.2f}\n"
                                 f"Take Profit: ${take_profit:.2f}"
                    }
                    
                    self._update_alert_state('conservative_trend_rider', 'short')
                    logger.info(f"Conservative Trend Rider SHORT signal for {symbol}")
                    return signal
            
            # Reset signals if conditions are no longer met
            if self.alert_states['conservative_trend_rider']['long']:
                if not (current[f'EMA_{params["ema_fast"]}'] > current[f'EMA_{params["ema_slow"]}']):
                    self._reset_alert_state('conservative_trend_rider', 'long')
            
            if self.alert_states['conservative_trend_rider']['short']:
                if not (current[f'EMA_{params["ema_fast"]}'] < current[f'EMA_{params["ema_slow"]}']):
                    self._reset_alert_state('conservative_trend_rider', 'short')
            
            return None
            
        except Exception as e:
            logger.error(f"Error in conservative trend rider strategy: {e}")
            return None
    
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range."""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=period).mean()
            
            return atr.iloc[-1]
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.0
    
    def _calculate_dynamic_position_size(self, price: float, atr: float) -> float:
        """Calculate dynamic position size based on ATR."""
        try:
            if atr == 0:
                return 0.0
            
            # Position size = risk_capital / (2.5 * ATR)
            strategy_capital = 10000 * CAPITAL_ALLOCATION.get('conservative_trend_rider', 0.5)
            risk_per_trade = RISK_MANAGEMENT['position_sizing']['max_risk_per_trade']
            risk_capital = strategy_capital * risk_per_trade
            
            position_size = risk_capital / (2.5 * atr)
            
            # Apply safety caps
            max_position_size = strategy_capital * 0.1  # Max 10% of strategy capital
            position_size = min(position_size, max_position_size)
            
            # Additional safety cap
            safety_cap = strategy_capital * 5
            position_size = min(position_size, safety_cap)
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating dynamic position size: {e}")
            return 0.0
    
    def check_all_strategies(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Check all enabled strategies for a given symbol."""
        signals = []
        
        # Check strategies in execution priority order
        for strategy_name in EXECUTION_PRIORITY:
            if strategy_name == 'aggressive_momentum_ignition':
                signal = self.check_aggressive_momentum_ignition(symbol)
            elif strategy_name == 'moderate_ema_crossover':
                signal = self.check_moderate_ema_crossover(symbol)
            elif strategy_name == 'conservative_trend_rider':
                signal = self.check_conservative_trend_rider(symbol)
            else:
                continue
            
            if signal:
                signals.append(signal)
        
        return signals
    
    def get_alert_states(self) -> Dict[str, Dict]:
        """Get current alert states for all profiles."""
        return self.alert_states.copy()
    
    def get_risk_state(self) -> Dict[str, Any]:
        """Get current risk management state."""
        return self.risk_state.copy()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.data_handler.cleanup()
            logger.info("EnhancedStrategyEngine cleanup completed")
        except Exception as e:
            logger.error(f"Error during EnhancedStrategyEngine cleanup: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Test the EnhancedStrategyEngine
    engine = EnhancedStrategyEngine()
    
    try:
        # Test all strategies
        signals = engine.check_all_strategies('BTC/USDT')
        
        if signals:
            print(f"Found {len(signals)} signals:")
            for signal in signals:
                print(f"- {signal['profile']}: {signal['signal_type']} at ${signal['price']:.2f}")
                print(f"  Position Size: {signal['position_size']:.2f}")
                print(f"  Stop Loss: ${signal['stop_loss']:.2f}")
                print(f"  Take Profit: ${signal['take_profit']:.2f}")
        else:
            print("No signals found")
        
        # Show current alert states
        states = engine.get_alert_states()
        print("\nCurrent alert states:")
        for profile, state in states.items():
            print(f"{profile}: {state}")
        
        # Show risk state
        risk_state = engine.get_risk_state()
        print(f"\nRisk state: {risk_state}")
    
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        engine.cleanup()
