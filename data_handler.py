"""
Data Handler Module for the Risk-Adaptive Crypto Trading Alert Bot.

This module handles all data fetching operations from cryptocurrency exchanges,
data preprocessing, and technical indicator calculations.
"""

import ccxt
import pandas as pd
import logging
import time
import numpy as np
from typing import Dict, List, Optional, Tuple

# Handle numpy compatibility for pandas-ta
try:
    import pandas_ta as ta
    # Test if pandas-ta can actually work
    test_data = pd.Series([1, 2, 3, 4, 5])
    test_ema = ta.ema(close=test_data, length=3)
    PANDAS_TA_AVAILABLE = True
    logger.info("pandas-ta successfully imported and tested")
except ImportError as e:
    logging.warning(f"pandas-ta not available: {e}")
    PANDAS_TA_AVAILABLE = False
except Exception as e:
    # Handle numpy compatibility issues
    if "cannot import name 'NaN'" in str(e) or "cannot import name" in str(e):
        logging.warning("pandas-ta has numpy compatibility issues, using fallback indicators")
        PANDAS_TA_AVAILABLE = False
    else:
        logging.warning(f"pandas-ta error: {e}")
        PANDAS_TA_AVAILABLE = False

from config import (
    EXCHANGE_NAME, EXCHANGE_SANDBOX, TRADING_PAIRS, CANDLE_LIMIT,
    REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY, DEBUG_MODE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataHandler:
    """
    Handles data fetching and preprocessing for the trading bot.
    
    This class manages connections to cryptocurrency exchanges, fetches OHLCV data,
    and calculates technical indicators for analysis.
    """
    
    def __init__(self):
        """Initialize the DataHandler with exchange connection."""
        self.exchange = None
        self._initialize_exchange()
        
    def _initialize_exchange(self) -> None:
        """
        Initialize the exchange connection using CCXT.
        
        Sets up connection to the specified exchange (default: Binance)
        with appropriate timeout and retry settings.
        """
        try:
            # Get the exchange class dynamically
            exchange_class = getattr(ccxt, EXCHANGE_NAME)
            
            # Initialize exchange with configuration
            self.exchange = exchange_class({
                'sandbox': EXCHANGE_SANDBOX,
                'timeout': REQUEST_TIMEOUT * 1000,  # CCXT expects milliseconds
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # Use spot trading by default
                }
            })
            
            logger.info(f"Successfully initialized {EXCHANGE_NAME} exchange connection")
            
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = None) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data from the exchange.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT')
            timeframe (str): Timeframe for the data (e.g., '5m', '15m', '1h', '1d')
            limit (int, optional): Number of candles to fetch. Defaults to CANDLE_LIMIT.
            
        Returns:
            Optional[pd.DataFrame]: DataFrame with OHLCV data or None if failed
            
        Raises:
            Exception: If data fetching fails after all retries
        """
        if limit is None:
            limit = CANDLE_LIMIT
            
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Fetching {limit} {timeframe} candles for {symbol} (attempt {attempt + 1})")
                
                # Fetch OHLCV data
                ohlcv_data = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit
                )
                
                if not ohlcv_data:
                    logger.warning(f"No data received for {symbol} on {timeframe}")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(
                    ohlcv_data,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Ensure data types are correct
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Remove any rows with NaN values
                df.dropna(inplace=True)
                
                if len(df) < 2:
                    logger.warning(f"Insufficient data for {symbol} on {timeframe}: {len(df)} candles")
                    return None
                
                logger.info(f"Successfully fetched {len(df)} {timeframe} candles for {symbol}")
                return df
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch data for {symbol} after {MAX_RETRIES} attempts")
                    raise
    
    def _calculate_stoch_rsi_fallback(self, close: pd.Series, k_period: int = 14, d_period: int = 3, rsi_length: int = 14) -> pd.DataFrame:
        """
        Calculate Stochastic RSI using fallback method when pandas-ta is not available.
        
        Args:
            close (pd.Series): Close price series
            k_period (int): %K period
            d_period (int): %D period
            rsi_length (int): RSI length
            
        Returns:
            pd.DataFrame: DataFrame with STOCHRSI columns
        """
        try:
            # Calculate RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_length).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_length).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Calculate Stochastic RSI
            rsi_min = rsi.rolling(window=k_period).min()
            rsi_max = rsi.rolling(window=k_period).max()
            stoch_rsi_k = 100 * (rsi - rsi_min) / (rsi_max - rsi_min)
            stoch_rsi_d = stoch_rsi_k.rolling(window=d_period).mean()
            
            # Create result DataFrame
            result = pd.DataFrame({
                f'STOCHRSIk_{k_period}_{d_period}_{rsi_length}': stoch_rsi_k,
                f'STOCHRSId_{k_period}_{d_period}_{rsi_length}': stoch_rsi_d
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating fallback Stochastic RSI: {e}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame({
                f'STOCHRSIk_{k_period}_{d_period}_{rsi_length}': [np.nan] * len(close),
                f'STOCHRSId_{k_period}_{d_period}_{rsi_length}': [np.nan] * len(close)
            })
    
    def _calculate_ema_fallback(self, close: pd.Series, length: int) -> pd.Series:
        """
        Calculate EMA using fallback method.
        
        Args:
            close (pd.Series): Close price series
            length (int): EMA length
            
        Returns:
            pd.Series: EMA values
        """
        try:
            return close.ewm(span=length, adjust=False).mean()
        except Exception as e:
            logger.error(f"Error calculating fallback EMA: {e}")
            return pd.Series([np.nan] * len(close), index=close.index)
    
    def _calculate_rsi_fallback(self, close: pd.Series, length: int = 14) -> pd.Series:
        """
        Calculate RSI using fallback method.
        
        Args:
            close (pd.Series): Close price series
            length (int): RSI length
            
        Returns:
            pd.Series: RSI values
        """
        try:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"Error calculating fallback RSI: {e}")
            return pd.Series([np.nan] * len(close), index=close.index)
    
    def _calculate_sma_fallback(self, close: pd.Series, length: int) -> pd.Series:
        """
        Calculate SMA using fallback method.
        
        Args:
            close (pd.Series): Close price series
            length (int): SMA length
            
        Returns:
            pd.Series: SMA values
        """
        try:
            return close.rolling(window=length).mean()
        except Exception as e:
            logger.error(f"Error calculating fallback SMA: {e}")
            return pd.Series([np.nan] * len(close), index=close.index)
    
    def calculate_indicators(self, df: pd.DataFrame, indicators: List[Dict]) -> pd.DataFrame:
        """
        Calculate technical indicators for the given DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data
            indicators (List[Dict]): List of indicator configurations
            
        Returns:
            pd.DataFrame: DataFrame with calculated indicators added
        """
        try:
            df_copy = df.copy()
            
            for indicator_config in indicators:
                indicator_name = indicator_config['name']
                
                if indicator_name == 'STOCHRSI':
                    # Calculate Stochastic RSI
                    k_period = indicator_config.get('k', 14)
                    d_period = indicator_config.get('d', 3)
                    rsi_length = indicator_config.get('rsi_length', 14)
                    
                    if PANDAS_TA_AVAILABLE:
                        try:
                            stoch_rsi = ta.stochrsi(
                                close=df_copy['close'],
                                k=k_period,
                                d=d_period,
                                rsi_length=rsi_length
                            )
                            df_copy = pd.concat([df_copy, stoch_rsi], axis=1)
                        except Exception as e:
                            logger.warning(f"pandas-ta STOCHRSI failed, using fallback: {e}")
                            stoch_rsi = self._calculate_stoch_rsi_fallback(
                                df_copy['close'], k_period, d_period, rsi_length
                            )
                            df_copy = pd.concat([df_copy, stoch_rsi], axis=1)
                    else:
                        stoch_rsi = self._calculate_stoch_rsi_fallback(
                            df_copy['close'], k_period, d_period, rsi_length
                        )
                        df_copy = pd.concat([df_copy, stoch_rsi], axis=1)
                    
                elif indicator_name == 'EMA':
                    # Calculate Exponential Moving Average
                    length = indicator_config.get('length', 20)
                    
                    if PANDAS_TA_AVAILABLE:
                        try:
                            ema = ta.ema(close=df_copy['close'], length=length)
                            df_copy[f'EMA_{length}'] = ema
                        except Exception as e:
                            logger.warning(f"pandas-ta EMA failed, using fallback: {e}")
                            df_copy[f'EMA_{length}'] = self._calculate_ema_fallback(df_copy['close'], length)
                    else:
                        df_copy[f'EMA_{length}'] = self._calculate_ema_fallback(df_copy['close'], length)
                    
                elif indicator_name == 'RSI':
                    # Calculate Relative Strength Index
                    length = indicator_config.get('length', 14)
                    
                    if PANDAS_TA_AVAILABLE:
                        try:
                            rsi = ta.rsi(close=df_copy['close'], length=length)
                            df_copy[f'RSI_{length}'] = rsi
                        except Exception as e:
                            logger.warning(f"pandas-ta RSI failed, using fallback: {e}")
                            df_copy[f'RSI_{length}'] = self._calculate_rsi_fallback(df_copy['close'], length)
                    else:
                        df_copy[f'RSI_{length}'] = self._calculate_rsi_fallback(df_copy['close'], length)
                    
                elif indicator_name == 'SMA':
                    # Calculate Simple Moving Average
                    length = indicator_config.get('length', 50)
                    
                    if PANDAS_TA_AVAILABLE:
                        try:
                            sma = ta.sma(close=df_copy['close'], length=length)
                            df_copy[f'SMA_{length}'] = sma
                        except Exception as e:
                            logger.warning(f"pandas-ta SMA failed, using fallback: {e}")
                            df_copy[f'SMA_{length}'] = self._calculate_sma_fallback(df_copy['close'], length)
                    else:
                        df_copy[f'SMA_{length}'] = self._calculate_sma_fallback(df_copy['close'], length)
                
                elif indicator_name == 'ADX':
                    # Calculate Average Directional Index
                    length = indicator_config.get('length', 14)
                    
                    if PANDAS_TA_AVAILABLE:
                        try:
                            adx = ta.adx(high=df_copy['high'], low=df_copy['low'], close=df_copy['close'], length=length)
                            df_copy[f'ADX_{length}'] = adx[f'ADX_{length}']
                        except Exception as e:
                            logger.warning(f"pandas-ta ADX failed, using fallback: {e}")
                            df_copy[f'ADX_{length}'] = self._calculate_adx_fallback(df_copy, length)
                    else:
                        df_copy[f'ADX_{length}'] = self._calculate_adx_fallback(df_copy, length)
                    
                else:
                    logger.warning(f"Unknown indicator: {indicator_name}")
            
            # Remove only rows where all indicator values are NaN (keep rows with some valid indicators)
            # This allows for partial indicator availability during warm-up periods
            indicator_columns = [col for col in df_copy.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
            if indicator_columns:
                # Only drop rows where ALL indicators are NaN
                df_copy = df_copy.dropna(subset=indicator_columns, how='all')
            
            if DEBUG_MODE:
                logger.debug(f"Calculated indicators. DataFrame shape: {df_copy.shape}")
                logger.debug(f"Available columns: {list(df_copy.columns)}")
            
            return df_copy
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            raise
    
    def get_multi_timeframe_data(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes simultaneously.
        
        Args:
            symbol (str): Trading pair symbol
            timeframes (List[str]): List of timeframes to fetch
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping timeframes to DataFrames
        """
        multi_tf_data = {}
        
        for timeframe in timeframes:
            try:
                df = self.fetch_ohlcv(symbol, timeframe)
                if df is not None:
                    multi_tf_data[timeframe] = df
                else:
                    logger.warning(f"Failed to fetch data for {timeframe}")
                    
            except Exception as e:
                logger.error(f"Error fetching {timeframe} data for {symbol}: {e}")
        
        return multi_tf_data
    
    def validate_data_quality(self, df: pd.DataFrame, min_candles: int = 50) -> bool:
        """
        Validate the quality of fetched data.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            min_candles (int): Minimum number of candles required
            
        Returns:
            bool: True if data quality is acceptable, False otherwise
        """
        if df is None or len(df) < min_candles:
            return False
        
        # Check for missing values
        if df.isnull().any().any():
            logger.warning("Data contains missing values")
            return False
        
        # Check for zero or negative prices
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if (df[col] <= 0).any():
                logger.warning(f"Data contains invalid prices in {col} column")
                return False
        
        # Check for reasonable price movements (e.g., no 1000% jumps)
        price_changes = df['close'].pct_change().abs()
        if (price_changes > 1.0).any():  # More than 100% change
            logger.warning("Data contains extreme price movements")
            return False
        
        return True
    
    def _calculate_adx_fallback(self, df: pd.DataFrame, length: int = 14) -> pd.Series:
        """Calculate ADX using fallback method when pandas-ta is not available."""
        try:
            import numpy as np
            import pandas as pd
            
            # Calculate True Range
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            true_range = pd.Series(np.maximum(high_low, np.maximum(high_close, low_close)), index=df.index)
            
            # Calculate Directional Movement
            up_move = df['high'] - df['high'].shift()
            down_move = df['low'].shift() - df['low']
            
            # Convert to pandas Series to ensure consistent indexing
            up_move = pd.Series(up_move, index=df.index)
            down_move = pd.Series(down_move, index=df.index)
            
            # Calculate DM+ and DM-
            plus_dm = pd.Series(0.0, index=df.index)
            minus_dm = pd.Series(0.0, index=df.index)
            
            # Set values where conditions are met
            plus_dm.loc[(up_move > down_move) & (up_move > 0)] = up_move.loc[(up_move > down_move) & (up_move > 0)]
            minus_dm.loc[(down_move > up_move) & (down_move > 0)] = down_move.loc[(down_move > up_move) & (down_move > 0)]
            
            # Smooth the values using exponential smoothing
            tr_smooth = true_range.ewm(span=length).mean()
            plus_dm_smooth = plus_dm.ewm(span=length).mean()
            minus_dm_smooth = minus_dm.ewm(span=length).mean()
            
            # Calculate DI+ and DI-
            plus_di = pd.Series(0.0, index=df.index)
            minus_di = pd.Series(0.0, index=df.index)
            
            # Avoid division by zero
            valid_tr = tr_smooth > 0
            plus_di.loc[valid_tr] = 100 * (plus_dm_smooth.loc[valid_tr] / tr_smooth.loc[valid_tr])
            minus_di.loc[valid_tr] = 100 * (minus_dm_smooth.loc[valid_tr] / tr_smooth.loc[valid_tr])
            
            # Calculate DX
            dx = pd.Series(0.0, index=df.index)
            denominator = plus_di + minus_di
            valid_denom = denominator > 0
            dx.loc[valid_denom] = 100 * np.abs(plus_di.loc[valid_denom] - minus_di.loc[valid_denom]) / denominator.loc[valid_denom]
            
            # Calculate ADX
            adx = dx.ewm(span=length).mean()
            
            return adx
            
        except Exception as e:
            logger.error(f"Error calculating ADX fallback: {e}")
            return pd.Series([np.nan] * len(df))
    
    def cleanup(self) -> None:
        """Clean up resources and close exchange connection."""
        try:
            if self.exchange:
                # Check if exchange has a close method before calling it
                if hasattr(self.exchange, 'close'):
                    self.exchange.close()
                    logger.info("Exchange connection closed")
                else:
                    logger.info("Exchange connection cleanup completed (no close method)")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Test the DataHandler
    handler = DataHandler()
    
    try:
        # Test fetching data for BTC/USDT
        df = handler.fetch_ohlcv('BTC/USDT', '5m', limit=100)
        
        if df is not None:
            print(f"Successfully fetched data: {df.shape}")
            print(df.head())
            
            # Test indicator calculation
            indicators = [
                {'name': 'STOCHRSI', 'k': 14, 'd': 3, 'rsi_length': 14},
                {'name': 'EMA', 'length': 20}
            ]
            
            df_with_indicators = handler.calculate_indicators(df, indicators)
            print(f"Data with indicators: {df_with_indicators.shape}")
            print(df_with_indicators.tail())
    
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        handler.cleanup()
