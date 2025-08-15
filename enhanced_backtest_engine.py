"""
Enhanced Backtesting Engine for the Risk-Adaptive Crypto Trading Alert Bot.

This module implements sophisticated backtesting for the enhanced strategies with:
- Multi-timeframe data analysis
- Advanced risk management simulation
- Position sizing algorithms
- Comprehensive performance metrics
- Strategy correlation analysis
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from data_handler import DataHandler
from config import (
    AGGRESSIVE_MOMENTUM_IGNITION, MODERATE_EMA_CROSSOVER, CONSERVATIVE_TREND_RIDER,
    CAPITAL_ALLOCATION, RISK_MANAGEMENT, BACKTEST_CONFIG, DEFAULT_PAIR
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedBacktestEngine:
    """
    Enhanced backtesting engine for sophisticated strategy evaluation.
    
    This class implements comprehensive backtesting for:
    1. Aggressive Momentum Ignition (5m) - High-frequency scalping
    2. Moderate EMA Crossover (15m) - Swing trading with 4h confirmation
    3. Conservative Trend Rider (4h) - Trend following with EMA/ADX/RSI
    """
    
    def __init__(self, initial_capital: float = 10000):
        """Initialize the EnhancedBacktestEngine."""
        self.data_handler = DataHandler()
        self.initial_capital = initial_capital
        self.results = {}
        
        logger.info(f"EnhancedBacktestEngine initialized with ${initial_capital:,.2f} initial capital")
    
    def run_comprehensive_backtest(self, symbol: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Run comprehensive backtest for all strategies.
        
        Args:
            symbol: Trading pair symbol (default: DEFAULT_PAIR)
            days: Number of days to backtest (default: 30)
        
        Returns:
            Dictionary containing backtest results for all strategies
        """
        if symbol is None:
            symbol = DEFAULT_PAIR
        
        logger.info(f"Starting comprehensive backtest for {symbol} over {days} days")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Run backtests for each strategy
            results = {}
            
            # 1. Aggressive Momentum Ignition (5m)
            logger.info("Running Aggressive Momentum Ignition backtest...")
            aggressive_results = self._backtest_aggressive_momentum_ignition(symbol, start_date, end_date)
            results['aggressive_momentum_ignition'] = aggressive_results
            
            # 2. Moderate EMA Crossover (15m)
            logger.info("Running Moderate EMA Crossover backtest...")
            moderate_results = self._backtest_moderate_ema_crossover(symbol, start_date, end_date)
            results['moderate_ema_crossover'] = moderate_results
            
            # 3. Conservative Trend Rider (4h)
            logger.info("Running Conservative Trend Rider backtest...")
            conservative_results = self._backtest_conservative_trend_rider(symbol, start_date, end_date)
            results['conservative_trend_rider'] = conservative_results
            
            # Calculate portfolio-level metrics
            portfolio_results = self._calculate_portfolio_metrics(results)
            results['portfolio'] = portfolio_results
            
            # Calculate strategy correlations
            correlation_matrix = self._calculate_strategy_correlations(results)
            results['correlations'] = correlation_matrix
            
            self.results = results
            logger.info("Comprehensive backtest completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive backtest: {e}")
            return {}
    
    def _backtest_aggressive_momentum_ignition(self, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Backtest the Aggressive Momentum Ignition strategy."""
        try:
            # Fetch 5-minute data
            df = self.data_handler.fetch_ohlcv(symbol, '5m', limit=10000)
            if df is None or len(df) < 100:
                logger.warning(f"Insufficient data for aggressive strategy backtest on {symbol}")
                return self._empty_backtest_result()
            
            # Filter data by date range
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            if len(df) < 50:
                logger.warning(f"Insufficient data in date range for aggressive strategy")
                return self._empty_backtest_result()
            
            # Calculate indicators
            params = AGGRESSIVE_MOMENTUM_IGNITION['parameters']
            indicators = [{
                'name': 'STOCHRSI',
                'k': params['stoch_rsi_k'],
                'd': params['stoch_rsi_d'],
                'rsi_length': params['rsi_length']
            }]
            
            df = self.data_handler.calculate_indicators(df, indicators)
            
            # Initialize backtest variables
            capital = self.initial_capital * CAPITAL_ALLOCATION['aggressive_momentum_ignition']
            position = None
            trades = []
            equity_curve = []
            
            # Run backtest
            for i in range(50, len(df)):
                current = df.iloc[i]
                previous = df.iloc[i-1]
                
                # Check for entry signals
                if position is None:
                    # Long signal
                    long_signal = self._check_aggressive_long_signal(previous, current, params)
                    if long_signal:
                        position = {
                            'type': 'long',
                            'entry_price': current['close'],
                            'entry_time': current.name,
                            'size': self._calculate_position_size(capital, current['close'], 
                                                                  current['close'] * 0.992, params['leverage'])
                        }
                        trades.append({
                            'entry_time': current.name,
                            'entry_price': current['close'],
                            'type': 'long',
                            'size': position['size']
                        })
                    
                    # Short signal
                    short_signal = self._check_aggressive_short_signal(previous, current, params)
                    if short_signal:
                        position = {
                            'type': 'short',
                            'entry_price': current['close'],
                            'entry_time': current.name,
                            'size': self._calculate_position_size(capital, current['close'], 
                                                                  current['close'] * 1.008, params['leverage'])
                        }
                        trades.append({
                            'entry_time': current.name,
                            'entry_price': current['close'],
                            'type': 'short',
                            'size': position['size']
                        })
                
                # Check for exit signals
                elif position is not None:
                    exit_signal = self._check_aggressive_exit_signal(current, position, params)
                    if exit_signal:
                        # Calculate P&L
                        if position['type'] == 'long':
                            pnl = (current['close'] - position['entry_price']) * position['size']
                        else:
                            pnl = (position['entry_price'] - current['close']) * position['size']
                        
                        # Update trade record
                        trades[-1].update({
                            'exit_time': current.name,
                            'exit_price': current['close'],
                            'pnl': pnl,
                            'return_pct': (pnl / (position['entry_price'] * position['size'])) * 100
                        })
                        
                        # Update capital
                        capital += pnl
                        position = None
                
                # Record equity
                current_equity = capital
                if position is not None:
                    if position['type'] == 'long':
                        current_equity += (current['close'] - position['entry_price']) * position['size']
                    else:
                        current_equity += (position['entry_price'] - current['close']) * position['size']
                
                equity_curve.append({
                    'timestamp': current.name,
                    'equity': current_equity
                })
            
            # Close any remaining position
            if position is not None:
                last_price = df.iloc[-1]['close']
                if position['type'] == 'long':
                    pnl = (last_price - position['entry_price']) * position['size']
                else:
                    pnl = (position['entry_price'] - last_price) * position['size']
                
                trades[-1].update({
                    'exit_time': df.iloc[-1].name,
                    'exit_price': last_price,
                    'pnl': pnl,
                    'return_pct': (pnl / (position['entry_price'] * position['size'])) * 100
                })
                capital += pnl
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics(trades, equity_curve, capital)
            
            return {
                'strategy': 'Aggressive Momentum Ignition',
                'timeframe': '5m',
                'trades': trades,
                'equity_curve': equity_curve,
                'final_capital': capital,
                'performance': performance
            }
            
        except Exception as e:
            logger.error(f"Error in aggressive momentum ignition backtest: {e}")
            return self._empty_backtest_result()
    
    def _check_aggressive_long_signal(self, previous: pd.Series, current: pd.Series, params: Dict) -> bool:
        """Check for aggressive long signal."""
        try:
            # StochRSI K crosses above D in oversold zone
            k_cross_above = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < 
                            previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] and
                            current[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > 
                            current[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'])
            
            both_oversold = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < params['oversold_threshold'] and
                            previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < params['oversold_threshold'])
            
            return k_cross_above and both_oversold
            
        except Exception as e:
            logger.error(f"Error checking aggressive long signal: {e}")
            return False
    
    def _check_aggressive_short_signal(self, previous: pd.Series, current: pd.Series, params: Dict) -> bool:
        """Check for aggressive short signal."""
        try:
            # StochRSI K crosses below D in overbought zone
            k_cross_below = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > 
                            previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] and
                            current[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] < 
                            current[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'])
            
            both_overbought = (previous[f'STOCHRSIk_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > params['overbought_threshold'] and
                               previous[f'STOCHRSId_{params["stoch_rsi_k"]}_{params["stoch_rsi_d"]}_{params["rsi_length"]}'] > params['overbought_threshold'])
            
            return k_cross_below and both_overbought
            
        except Exception as e:
            logger.error(f"Error checking aggressive short signal: {e}")
            return False
    
    def _check_aggressive_exit_signal(self, current: pd.Series, position: Dict, params: Dict) -> bool:
        """Check for aggressive exit signal."""
        try:
            # Time-based exit (15 minutes)
            time_in_trade = current.name - position['entry_time']
            if time_in_trade >= timedelta(minutes=15):
                return True
            
            # Take profit (1.5%)
            if position['type'] == 'long':
                if current['close'] >= position['entry_price'] * 1.015:
                    return True
            else:
                if current['close'] <= position['entry_price'] * 0.985:
                    return True
            
            # Stop loss (0.8%)
            if position['type'] == 'long':
                if current['close'] <= position['entry_price'] * 0.992:
                    return True
            else:
                if current['close'] >= position['entry_price'] * 1.008:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking aggressive exit signal: {e}")
            return False
    
    def _backtest_moderate_ema_crossover(self, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Backtest the Moderate EMA Crossover strategy."""
        try:
            # Fetch multi-timeframe data
            timeframes = ['15m', '4h']
            multi_tf_data = self.data_handler.get_multi_timeframe_data(symbol, timeframes)
            
            if '15m' not in multi_tf_data or '4h' not in multi_tf_data:
                logger.warning(f"Failed to fetch multi-timeframe data for moderate strategy")
                return self._empty_backtest_result()
            
            df_15m = multi_tf_data['15m']
            df_4h = multi_tf_data['4h']
            
            # Filter data by date range
            df_15m = df_15m[(df_15m.index >= start_date) & (df_15m.index <= end_date)]
            df_4h = df_4h[(df_4h.index >= start_date) & (df_4h.index <= end_date)]
            
            if len(df_15m) < 50 or len(df_4h) < 50:
                logger.warning(f"Insufficient data in date range for moderate strategy")
                return self._empty_backtest_result()
            
            # Calculate indicators
            params = MODERATE_EMA_CROSSOVER['parameters']
            indicators_15m = [
                {'name': 'EMA', 'length': params['ema_fast']},
                {'name': 'EMA', 'length': params['ema_slow']},
                {'name': 'RSI', 'length': params['rsi_length']}
            ]
            
            df_15m = self.data_handler.calculate_indicators(df_15m, indicators_15m)
            df_4h = self.data_handler.calculate_indicators(df_4h, [{'name': 'EMA', 'length': params['trend_ema']}])
            
            # Initialize backtest variables
            capital = self.initial_capital * CAPITAL_ALLOCATION['moderate_ema_crossover']
            position = None
            trades = []
            equity_curve = []
            
            # Run backtest
            for i in range(50, len(df_15m)):
                current_15m = df_15m.iloc[i]
                previous_15m = df_15m.iloc[i-1]
                
                # Find corresponding 4h data
                current_4h = self._find_closest_4h_data(df_4h, current_15m.name)
                if current_4h is None:
                    continue
                
                # Check for entry signals
                if position is None:
                    # Long signal
                    long_signal = self._check_moderate_long_signal(current_15m, previous_15m, current_4h, params)
                    if long_signal:
                        position = {
                            'type': 'long',
                            'entry_price': current_15m['close'],
                            'entry_time': current_15m.name,
                            'size': self._calculate_position_size(capital, current_15m['close'], 
                                                                  current_15m['close'] * 0.985, params['leverage'])
                        }
                        trades.append({
                            'entry_time': current_15m.name,
                            'entry_price': current_15m['close'],
                            'type': 'long',
                            'size': position['size']
                        })
                    
                    # Short signal
                    short_signal = self._check_moderate_short_signal(current_15m, previous_15m, current_4h, params)
                    if short_signal:
                        position = {
                            'type': 'short',
                            'entry_price': current_15m['close'],
                            'entry_time': current_15m.name,
                            'size': self._calculate_position_size(capital, current_15m['close'], 
                                                                  current_15m['close'] * 1.015, params['leverage'])
                        }
                        trades.append({
                            'entry_time': current_15m.name,
                            'entry_price': current_15m['close'],
                            'type': 'short',
                            'size': position['size']
                        })
                
                # Check for exit signals
                elif position is not None:
                    exit_signal = self._check_moderate_exit_signal(current_15m, position, params)
                    if exit_signal:
                        # Calculate P&L
                        if position['type'] == 'long':
                            pnl = (current_15m['close'] - position['entry_price']) * position['size']
                        else:
                            pnl = (position['entry_price'] - current_15m['close']) * position['size']
                        
                        # Update trade record
                        trades[-1].update({
                            'exit_time': current_15m.name,
                            'exit_price': current_15m['close'],
                            'pnl': pnl,
                            'return_pct': (pnl / (position['entry_price'] * position['size'])) * 100
                        })
                        
                        # Update capital
                        capital += pnl
                        position = None
                
                # Record equity
                current_equity = capital
                if position is not None:
                    if position['type'] == 'long':
                        current_equity += (current_15m['close'] - position['entry_price']) * position['size']
                    else:
                        current_equity += (position['entry_price'] - current_15m['close']) * position['size']
                
                equity_curve.append({
                    'timestamp': current_15m.name,
                    'equity': current_equity
                })
            
            # Close any remaining position
            if position is not None:
                last_price = df_15m.iloc[-1]['close']
                if position['type'] == 'long':
                    pnl = (last_price - position['entry_price']) * position['size']
                else:
                    pnl = (position['entry_price'] - last_price) * position['size']
                
                trades[-1].update({
                    'exit_time': df_15m.iloc[-1].name,
                    'exit_price': last_price,
                    'pnl': pnl,
                    'return_pct': (pnl / (position['entry_price'] * position['size'])) * 100
                })
                capital += pnl
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics(trades, equity_curve, capital)
            
            return {
                'strategy': 'Moderate EMA Crossover',
                'timeframe': '15m',
                'trades': trades,
                'equity_curve': equity_curve,
                'final_capital': capital,
                'performance': performance
            }
            
        except Exception as e:
            logger.error(f"Error in moderate EMA crossover backtest: {e}")
            return self._empty_backtest_result()
    
    def _check_moderate_long_signal(self, current: pd.Series, previous: pd.Series, current_4h: pd.Series, params: Dict) -> bool:
        """Check for moderate long signal."""
        try:
            # EMA fast > EMA slow
            ema_bullish = current[f'EMA_{params["ema_fast"]}'] > current[f'EMA_{params["ema_slow"]}']
            
            # EMA slope positive
            ema_slope_bullish = current[f'EMA_{params["ema_fast"]}'] > previous[f'EMA_{params["ema_fast"]}']
            
            # RSI > bullish threshold
            rsi_bullish = current[f'RSI_{params["rsi_length"]}'] > params['rsi_bullish']
            
            # Price > open (bullish candle)
            candle_bullish = current['close'] > current['open']
            
            # Price > 4h trend EMA
            trend_bullish = current['close'] > current_4h[f'EMA_{params["trend_ema"]}']
            
            return ema_bullish and ema_slope_bullish and rsi_bullish and candle_bullish and trend_bullish
            
        except Exception as e:
            logger.error(f"Error checking moderate long signal: {e}")
            return False
    
    def _check_moderate_short_signal(self, current: pd.Series, previous: pd.Series, current_4h: pd.Series, params: Dict) -> bool:
        """Check for moderate short signal."""
        try:
            # EMA fast < EMA slow
            ema_bearish = current[f'EMA_{params["ema_fast"]}'] < current[f'EMA_{params["ema_slow"]}']
            
            # EMA slope negative
            ema_slope_bearish = current[f'EMA_{params["ema_fast"]}'] < previous[f'EMA_{params["ema_fast"]}']
            
            # RSI < bearish threshold
            rsi_bearish = current[f'RSI_{params["rsi_length"]}'] < params['rsi_bearish']
            
            # Price < open (bearish candle)
            candle_bearish = current['close'] < current['open']
            
            # Price < 4h trend EMA
            trend_bearish = current['close'] < current_4h[f'EMA_{params["trend_ema"]}']
            
            return ema_bearish and ema_slope_bearish and rsi_bearish and candle_bearish and trend_bearish
            
        except Exception as e:
            logger.error(f"Error checking moderate short signal: {e}")
            return False
    
    def _check_moderate_exit_signal(self, current: pd.Series, position: Dict, params: Dict) -> bool:
        """Check for moderate exit signal."""
        try:
            # Take profit (2.5x risk-reward)
            if position['type'] == 'long':
                if current['close'] >= position['entry_price'] * 1.0375:
                    return True
            else:
                if current['close'] <= position['entry_price'] * 0.9625:
                    return True
            
            # Stop loss (1.5%)
            if position['type'] == 'long':
                if current['close'] <= position['entry_price'] * 0.985:
                    return True
            else:
                if current['close'] >= position['entry_price'] * 1.015:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking moderate exit signal: {e}")
            return False
    
    def _backtest_conservative_trend_rider(self, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Backtest the Conservative Trend Rider strategy."""
        try:
            # Fetch 4-hour data (need more data for EMA200 and ADX calculations)
            df = self.data_handler.fetch_ohlcv(symbol, '4h', limit=300)
            if df is None or len(df) < 250:
                logger.warning(f"Insufficient data for conservative trend rider backtest on {symbol}")
                return self._empty_backtest_result()
            
            # Filter data by date range
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            if len(df) < 50:
                logger.warning(f"Insufficient data in date range for conservative trend rider")
                return self._empty_backtest_result()
            
            # Calculate EMAs and ADX
            params = CONSERVATIVE_TREND_RIDER['parameters']
            indicators = [
                {'name': 'EMA', 'length': params['ema_fast']},
                {'name': 'EMA', 'length': params['ema_slow']},
                {'name': 'ADX', 'length': 14},
                {'name': 'RSI', 'length': params['rsi_length']}
            ]
            
            df = self.data_handler.calculate_indicators(df, indicators)
            
            # Initialize backtest variables
            capital = self.initial_capital * CAPITAL_ALLOCATION['conservative_trend_rider']
            position = None
            trades = []
            equity_curve = []
            
            # Run backtest
            for i in range(3, len(df)):  # Need at least 3 periods for confirmation
                current = df.iloc[i]
                previous = df.iloc[i-1]
                prev_prev = df.iloc[i-2]
                
                # Check for entry signals
                if position is None:
                    # Long signal
                    long_signal = self._check_conservative_long_signal(current, previous, prev_prev, params)
                    if long_signal:
                        atr = self._calculate_atr(df.iloc[:i+1], 14)
                        position_size = self._calculate_dynamic_position_size(current['close'], atr)
                        
                        # Initialize trailing stop and profit scaling
                        atr = self._calculate_atr(df.iloc[:i+1], 14)
                        trailing_stop_multiplier = CONSERVATIVE_TREND_RIDER['exit_conditions']['trailing_stop_multiplier']
                        trailing_stop = current['close'] - (trailing_stop_multiplier * atr)
                        
                        position = {
                            'type': 'long',
                            'entry_price': current['close'],
                            'entry_time': current.name,
                            'size': position_size,
                            'trailing_stop': trailing_stop,
                            'profit_scaling_levels': CONSERVATIVE_TREND_RIDER['exit_conditions']['profit_scaling_levels'].copy()
                        }
                        trades.append({
                            'entry_time': current.name,
                            'entry_price': current['close'],
                            'type': 'long',
                            'size': position_size
                        })
                    
                    # Short signal
                    short_signal = self._check_conservative_short_signal(current, previous, prev_prev, params)
                    if short_signal:
                        atr = self._calculate_atr(df.iloc[:i+1], 14)
                        position_size = self._calculate_dynamic_position_size(current['close'], atr)
                        
                        # Initialize trailing stop and profit scaling
                        atr = self._calculate_atr(df.iloc[:i+1], 14)
                        trailing_stop_multiplier = CONSERVATIVE_TREND_RIDER['exit_conditions']['trailing_stop_multiplier']
                        trailing_stop = current['close'] + (trailing_stop_multiplier * atr)
                        
                        position = {
                            'type': 'short',
                            'entry_price': current['close'],
                            'entry_time': current.name,
                            'size': position_size,
                            'trailing_stop': trailing_stop,
                            'profit_scaling_levels': CONSERVATIVE_TREND_RIDER['exit_conditions']['profit_scaling_levels'].copy()
                        }
                        trades.append({
                            'entry_time': current.name,
                            'entry_price': current['close'],
                            'type': 'short',
                            'size': position_size
                        })
                
                # Check for exit signals
                elif position is not None:
                    exit_signal = self._check_conservative_exit_signal(current, position, params)
                    if exit_signal:
                        # Calculate P&L
                        if position['type'] == 'long':
                            pnl = (current['close'] - position['entry_price']) * position['size']
                        else:
                            pnl = (position['entry_price'] - current['close']) * position['size']
                        
                        # Update trade record
                        trades[-1].update({
                            'exit_time': current.name,
                            'exit_price': current['close'],
                            'pnl': pnl,
                            'return_pct': (pnl / (position['entry_price'] * position['size'])) * 100
                        })
                        
                        # Update capital
                        capital += pnl
                        position = None
                    
                    # Check for trailing stop updates
                    elif CONSERVATIVE_TREND_RIDER['filters'].get('trailing_stop', False):
                        self._update_trailing_stop(position, current, df.iloc[:i+1])
                    
                    # Check for profit scaling exits
                    elif CONSERVATIVE_TREND_RIDER['filters'].get('profit_scaling', False):
                        if self._check_profit_scaling_exit(position, current):
                            # Partial exit logic
                            partial_exit = self._execute_profit_scaling_exit(position, current)
                            if partial_exit:
                                capital += partial_exit['pnl']
                                position['size'] -= partial_exit['size_reduced']
                
                # Record equity
                current_equity = capital
                if position is not None:
                    if position['type'] == 'long':
                        current_equity += (current['close'] - position['entry_price']) * position['size']
                    else:
                        current_equity += (position['entry_price'] - current['close']) * position['size']
                
                equity_curve.append({
                    'timestamp': current.name,
                    'equity': current_equity
                })
            
            # Close any remaining position
            if position is not None:
                last_price = df.iloc[-1]['close']
                if position['type'] == 'long':
                    pnl = (last_price - position['entry_price']) * position['size']
                else:
                    pnl = (position['entry_price'] - last_price) * position['size']
                
                trades[-1].update({
                    'exit_time': df.iloc[-1].name,
                    'exit_price': last_price,
                    'pnl': pnl,
                    'return_pct': (pnl / (position['entry_price'] * position['size'])) * 100
                })
                capital += pnl
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics(trades, equity_curve, capital)
            
            # Ensure final capital is valid
            if np.isnan(capital) or np.isinf(capital):
                capital = self.initial_capital * CAPITAL_ALLOCATION['conservative_trend_rider']
            
            return {
                'strategy': 'Conservative Trend Rider',
                'timeframe': '4h',
                'trades': trades,
                'equity_curve': equity_curve,
                'final_capital': capital,
                'performance': performance
            }
            
        except Exception as e:
            logger.error(f"Error in conservative trend rider backtest: {e}")
            return self._empty_backtest_result()
    
    def _check_conservative_long_signal(self, current: pd.Series, previous: pd.Series, prev_prev: pd.Series, params: Dict) -> bool:
        """Check for conservative trend rider long signal."""
        try:
            # EMA fast > EMA slow
            ema_bullish = current[f'EMA_{params["ema_fast"]}'] > current[f'EMA_{params["ema_slow"]}']
            
            # Price above slow EMA
            price_above_ema = current['close'] > current[f'EMA_{params["ema_slow"]}']
            
            # Strong trend (ADX > threshold)
            strong_trend = current['ADX_14'] > params['adx_threshold']
            
            # Good entry (RSI < upper threshold)
            good_entry = current[f'RSI_{params["rsi_length"]}'] < params['rsi_upper']
            
            return ema_bullish and price_above_ema and strong_trend and good_entry
            
        except Exception as e:
            logger.error(f"Error checking conservative long signal: {e}")
            return False
    
    def _check_conservative_short_signal(self, current: pd.Series, previous: pd.Series, prev_prev: pd.Series, params: Dict) -> bool:
        """Check for conservative trend rider short signal."""
        try:
            # EMA fast < EMA slow
            ema_bearish = current[f'EMA_{params["ema_fast"]}'] < current[f'EMA_{params["ema_slow"]}']
            
            # Price below slow EMA
            price_below_ema = current['close'] < current[f'EMA_{params["ema_slow"]}']
            
            # Strong trend (ADX > threshold)
            strong_trend = current['ADX_14'] > params['adx_threshold']
            
            # Good entry (RSI > lower threshold)
            good_entry = current[f'RSI_{params["rsi_length"]}'] > params['rsi_lower']
            
            return ema_bearish and price_below_ema and strong_trend and good_entry
            
        except Exception as e:
            logger.error(f"Error checking conservative short signal: {e}")
            return False
    
    def _check_conservative_exit_signal(self, current: pd.Series, position: Dict, params: Dict) -> bool:
        """Check for conservative trend rider exit signal."""
        try:
            # Take profit (3:1 risk-reward ratio)
            if position['type'] == 'long':
                # Calculate risk and take profit
                risk = position['entry_price'] - position.get('stop_loss', position['entry_price'] * 0.99)
                take_profit = position['entry_price'] + (3 * risk)
                if current['close'] >= take_profit:
                    return True
            else:
                # Calculate risk and take profit
                risk = position.get('stop_loss', position['entry_price'] * 1.01) - position['entry_price']
                take_profit = position['entry_price'] - (3 * risk)
                if current['close'] <= take_profit:
                    return True
            
            # Stop loss (EMA crossover)
            if position['type'] == 'long':
                if current[f'EMA_{params["ema_fast"]}'] < current[f'EMA_{params["ema_slow"]}']:
                    return True
            else:
                if current[f'EMA_{params["ema_fast"]}'] > current[f'EMA_{params["ema_slow"]}']:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking conservative exit signal: {e}")
            return False
    
    def _find_closest_4h_data(self, df_4h: pd.DataFrame, timestamp: datetime) -> Optional[pd.Series]:
        """Find the closest 4h data point to a given timestamp."""
        try:
            # Find the most recent 4h candle before or at the given timestamp
            available_data = df_4h[df_4h.index <= timestamp]
            if len(available_data) > 0:
                return available_data.iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error finding closest 4h data: {e}")
            return None
    
    def _calculate_position_size(self, capital: float, entry_price: float, stop_loss: float, leverage: int) -> float:
        """Calculate position size based on risk management."""
        try:
            risk_per_trade = RISK_MANAGEMENT['position_sizing']['max_risk_per_trade']
            risk_amount = capital * risk_per_trade
            
            # Calculate position size based on absolute price risk
            price_risk = abs(entry_price - stop_loss)
            if price_risk == 0:
                return 0.0
            
            position_size = risk_amount / price_risk
            
            # Apply leverage caps
            max_position_size = capital * leverage
            position_size = min(position_size, max_position_size)
            
            # Additional safety cap - position size should not exceed 10x the capital
            safety_cap = capital * 10
            position_size = min(position_size, safety_cap)
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def _calculate_dynamic_position_size(self, price: float, atr: float) -> float:
        """Calculate dynamic position size based on ATR."""
        try:
            # Handle edge cases
            if atr == 0 or atr < 0.0001:  # Minimum ATR threshold
                atr = 0.0001
            
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
            
            # Ensure position size is reasonable
            if position_size <= 0 or np.isnan(position_size) or np.isinf(position_size):
                return 0.0
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating dynamic position size: {e}")
            return 0.0
    
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range."""
        try:
            if len(df) < period:
                return 0.001  # Return minimum ATR if insufficient data
            
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=period).mean()
            
            atr_value = atr.iloc[-1]
            
            # Handle NaN and extreme values
            if pd.isna(atr_value) or atr_value <= 0:
                return 0.001  # Minimum ATR value
            
            return atr_value
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.001
    
    def _update_trailing_stop(self, position: Dict, current: pd.Series, df: pd.DataFrame) -> None:
        """Update trailing stop for a position."""
        try:
            if not position or 'trailing_stop' not in position:
                return
            
            atr = self._calculate_atr(df, 14)
            multiplier = CONSERVATIVE_TREND_RIDER['exit_conditions']['trailing_stop_multiplier']
            
            if position['type'] == 'long':
                new_trailing_stop = current['close'] - (multiplier * atr)
                if new_trailing_stop > position['trailing_stop']:
                    position['trailing_stop'] = new_trailing_stop
            else:  # short
                new_trailing_stop = current['close'] + (multiplier * atr)
                if new_trailing_stop < position['trailing_stop']:
                    position['trailing_stop'] = new_trailing_stop
                    
        except Exception as e:
            logger.error(f"Error updating trailing stop: {e}")
    
    def _check_profit_scaling_exit(self, position: Dict, current: pd.Series) -> bool:
        """Check if profit scaling exit conditions are met."""
        try:
            if not position or 'profit_scaling_levels' not in position:
                return False
            
            entry_price = position['entry_price']
            current_price = current['close']
            
            if position['type'] == 'long':
                profit_ratio = current_price / entry_price
            else:  # short
                profit_ratio = entry_price / current_price
            
            # Check if any profit scaling level is reached
            for level in position['profit_scaling_levels']:
                if profit_ratio >= level['threshold'] and not level.get('executed', False):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking profit scaling exit: {e}")
            return False
    
    def _execute_profit_scaling_exit(self, position: Dict, current: pd.Series) -> Optional[Dict]:
        """Execute partial profit scaling exit."""
        try:
            if not position or 'profit_scaling_levels' not in position:
                return None
            
            entry_price = position['entry_price']
            current_price = current['close']
            
            if position['type'] == 'long':
                profit_ratio = current_price / entry_price
            else:  # short
                profit_ratio = entry_price / current_price
            
            # Find the highest level reached
            for level in reversed(position['profit_scaling_levels']):
                if profit_ratio >= level['threshold'] and not level.get('executed', False):
                    # Execute partial exit
                    exit_size = position['size'] * (level['close_pct'] / 100)
                    if position['type'] == 'long':
                        pnl = (current_price - entry_price) * exit_size
                    else:
                        pnl = (entry_price - current_price) * exit_size
                    
                    # Mark level as executed
                    level['executed'] = True
                    
                    return {
                        'size_reduced': exit_size,
                        'pnl': pnl,
                        'level': level
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing profit scaling exit: {e}")
            return None
    
    def _calculate_performance_metrics(self, trades: List[Dict], equity_curve: List[Dict], final_capital: float) -> Dict[str, float]:
        """Calculate comprehensive performance metrics."""
        try:
            if not trades:
                return self._empty_backtest_result()
            
            # Basic metrics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
            losing_trades = len([t for t in trades if t.get('pnl', 0) < 0])
            
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # P&L metrics
            total_pnl = sum(t.get('pnl', 0) for t in trades)
            avg_win = np.mean([t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]) if losing_trades > 0 else 0
            
            # Handle edge cases for profit factor
            if avg_loss == 0:
                profit_factor = float('inf') if avg_win > 0 else 0.0
            else:
                profit_factor = abs(avg_win / avg_loss)
            
            # Return metrics - handle extreme values
            try:
                if self.initial_capital <= 0:
                    total_return = 0.0
                else:
                    total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
                    # Cap extreme returns to prevent overflow
                    if abs(total_return) > 1000000:  # Cap at 1,000,000%
                        total_return = 1000000 if total_return > 0 else -1000000
                    # Handle NaN and infinite values
                    if np.isnan(total_return) or np.isinf(total_return):
                        total_return = 0.0
            except (ZeroDivisionError, OverflowError, ValueError):
                total_return = 0.0
            
            # Risk metrics
            returns = [t.get('return_pct', 0) for t in trades]
            # Filter out extreme values
            returns = [r for r in returns if abs(r) < 1000000]
            
            volatility = np.std(returns) if len(returns) > 1 else 0
            sharpe_ratio = (np.mean(returns) / volatility) if volatility > 0 else 0
            
            # Cap Sharpe ratio to prevent extreme values
            if abs(sharpe_ratio) > 100:
                sharpe_ratio = 100 if sharpe_ratio > 0 else -100
            
            # Drawdown calculation
            equity_values = [e['equity'] for e in equity_curve]
            if not equity_values:
                max_drawdown_pct = 0.0
            else:
                peak = equity_values[0]
                max_drawdown = 0
                
                for equity in equity_values:
                    if equity > peak:
                        peak = equity
                    if peak > 0:  # Prevent division by zero
                        drawdown = (peak - equity) / peak
                        max_drawdown = max(max_drawdown, drawdown)
                
                max_drawdown_pct = max_drawdown * 100
                # Cap drawdown to prevent extreme values
                if max_drawdown_pct > 1000000:
                    max_drawdown_pct = 1000000
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'total_return_pct': total_return,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown_pct': max_drawdown_pct,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return self._empty_performance_metrics()
    
    def _calculate_portfolio_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio-level performance metrics."""
        try:
            portfolio_capital = 0
            total_return = 0
            strategy_weights = []
            
            for strategy_name, result in results.items():
                if strategy_name in ['portfolio', 'correlations']:
                    continue
                
                if 'final_capital' in result:
                    portfolio_capital += result['final_capital']
                    strategy_weight = CAPITAL_ALLOCATION.get(strategy_name, 0.33)
                    strategy_weights.append(strategy_weight)
            
            if portfolio_capital > 0:
                total_return = ((portfolio_capital - self.initial_capital) / self.initial_capital) * 100
            
            return {
                'initial_capital': self.initial_capital,
                'final_capital': portfolio_capital,
                'total_return_pct': total_return,
                'strategy_weights': strategy_weights
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {}
    
    def _calculate_strategy_correlations(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate correlations between strategies."""
        try:
            correlations = {}
            strategies = [k for k in results.keys() if k not in ['portfolio', 'correlations']]
            
            for i, strategy1 in enumerate(strategies):
                for strategy2 in strategies[i+1:]:
                    if 'equity_curve' in results[strategy1] and 'equity_curve' in results[strategy2]:
                        try:
                            # Extract equity values and align timestamps
                            equity1 = pd.DataFrame(results[strategy1]['equity_curve'])
                            equity2 = pd.DataFrame(results[strategy2]['equity_curve'])
                            
                            # Check if timestamp column exists
                            if 'timestamp' not in equity1.columns or 'timestamp' not in equity2.columns:
                                continue
                            
                            # Merge on timestamp and calculate correlation
                            merged = pd.merge(equity1, equity2, on='timestamp', suffixes=('_1', '_2'))
                            if len(merged) > 1:
                                # Check if equity columns exist
                                if 'equity_1' in merged.columns and 'equity_2' in merged.columns:
                                    corr = merged['equity_1'].corr(merged['equity_2'])
                                    correlations[f"{strategy1}_vs_{strategy2}"] = corr if not pd.isna(corr) else 0.0
                        except Exception as e:
                            logger.warning(f"Could not calculate correlation between {strategy1} and {strategy2}: {e}")
                            continue
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating strategy correlations: {e}")
            return {}
    
    def _empty_backtest_result(self) -> Dict[str, Any]:
        """Return empty backtest result structure."""
        return {
            'strategy': 'Unknown',
            'timeframe': 'Unknown',
            'trades': [],
            'equity_curve': [],
            'final_capital': self.initial_capital,
            'performance': self._empty_performance_metrics()
        }
    
    def _empty_performance_metrics(self) -> Dict[str, float]:
        """Return empty performance metrics structure."""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'total_return_pct': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown_pct': 0.0,
            'volatility': 0.0
        }
    
    def print_backtest_report(self, results: Dict[str, Any] = None) -> None:
        """Print comprehensive backtest report."""
        if results is None:
            results = self.results
        
        if not results:
            print("No backtest results available.")
            return
        
        print("\n" + "="*80)
        print("🚀 ENHANCED STRATEGY BACKTEST REPORT")
        print("="*80)
        
        # Print individual strategy results
        for strategy_name, result in results.items():
            if strategy_name in ['portfolio', 'correlations']:
                continue
            
            if 'performance' in result:
                perf = result['performance']
                print(f"\n📊 {result['strategy']} ({result['timeframe']})")
                print("-" * 50)
                print(f"Total Trades: {perf['total_trades']}")
                print(f"Win Rate: {perf['win_rate']:.1f}%")
                print(f"Total Return: {perf['total_return_pct']:.2f}%")
                print(f"Profit Factor: {perf['profit_factor']:.2f}")
                print(f"Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
                print(f"Max Drawdown: {perf['max_drawdown_pct']:.2f}%")
                print(f"Final Capital: ${result['final_capital']:,.2f}")
        
        # Print portfolio results
        if 'portfolio' in results:
            portfolio = results['portfolio']
            print(f"\n💼 PORTFOLIO SUMMARY")
            print("-" * 50)
            print(f"Initial Capital: ${portfolio['initial_capital']:,.2f}")
            print(f"Final Capital: ${portfolio['final_capital']:,.2f}")
            print(f"Total Return: {portfolio['total_return_pct']:.2f}%")
        
        # Print correlations
        if 'correlations' in results:
            correlations = results['correlations']
            if correlations:
                print(f"\n🔗 STRATEGY CORRELATIONS")
                print("-" * 50)
                for pair, corr in correlations.items():
                    print(f"{pair}: {corr:.3f}")
        
        print("\n" + "="*80)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.data_handler.cleanup()
            logger.info("EnhancedBacktestEngine cleanup completed")
        except Exception as e:
            logger.error(f"Error during EnhancedBacktestEngine cleanup: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Test the EnhancedBacktestEngine
    engine = EnhancedBacktestEngine(initial_capital=10000)
    
    try:
        # Run comprehensive backtest
        results = engine.run_comprehensive_backtest('BTC/USDT', days=30)
        
        # Print results
        engine.print_backtest_report(results)
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        engine.cleanup()
