#!/usr/bin/env python3
"""
Enhanced Backtesting Runner for the Risk-Adaptive Crypto Trading Alert Bot.

This script runs comprehensive backtests for the enhanced strategies:
1. Aggressive Momentum Ignition (5m) - High-frequency scalping
2. Moderate EMA Crossover (15m) - Swing trading with 4h confirmation
3. Conservative Trend Setter (1d) - Position sizing engine

Usage:
    python3 run_enhanced_backtest.py [symbol] [days]
    
Examples:
    python3 run_enhanced_backtest.py                    # Default: BTC/USDT, 30 days
    python3 run_enhanced_backtest.py ETH/USDT          # ETH/USDT, 30 days
    python3 run_enhanced_backtest.py BTC/USDT 60       # BTC/USDT, 60 days
"""

import sys
import argparse
from datetime import datetime
from enhanced_backtest_engine import EnhancedBacktestEngine
from config import DEFAULT_PAIR, CAPITAL_ALLOCATION, RISK_MANAGEMENT


def main():
    """Main function to run enhanced backtesting."""
    parser = argparse.ArgumentParser(
        description='Run enhanced backtesting for sophisticated trading strategies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_enhanced_backtest.py                    # Default: BTC/USDT, 30 days
  python3 run_enhanced_backtest.py ETH/USDT          # ETH/USDT, 30 days
  python3 run_enhanced_backtest.py BTC/USDT 60       # BTC/USDT, 60 days
  python3 run_enhanced_backtest.py SOL/USDT 90       # SOL/USDT, 90 days
        """
    )
    
    parser.add_argument('symbol', nargs='?', default=DEFAULT_PAIR,
                       help=f'Trading pair symbol (default: {DEFAULT_PAIR})')
    parser.add_argument('days', nargs='?', type=int, default=30,
                       help='Number of days to backtest (default: 30)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.days < 7:
        print("❌ Error: Minimum backtest period is 7 days")
        sys.exit(1)
    
    if args.days > 365:
        print("⚠️  Warning: Backtesting over 1 year may take significant time")
    
    print("🚀 ENHANCED STRATEGY BACKTESTING")
    print("=" * 60)
    print(f"Symbol: {args.symbol}")
    print(f"Period: {args.days} days")
    print(f"Initial Capital: $10,000")
    print(f"Capital Allocation:")
    for strategy, allocation in CAPITAL_ALLOCATION.items():
        print(f"  {strategy}: {allocation*100:.0f}% (${allocation*10000:,.0f})")
    print(f"Risk Management:")
    print(f"  Max Risk per Trade: {RISK_MANAGEMENT['position_sizing']['max_risk_per_trade']*100:.1f}%")
    print(f"  Daily Loss Limit: {RISK_MANAGEMENT['daily_loss_limit']*100:.1f}%")
    print(f"  Max Portfolio Risk: {RISK_MANAGEMENT['position_sizing']['max_portfolio_risk']*100:.1f}%")
    print("=" * 60)
    
    # Initialize backtesting engine
    print("\n🔧 Initializing Enhanced Backtesting Engine...")
    engine = EnhancedBacktestEngine(initial_capital=10000)
    
    try:
        # Run comprehensive backtest
        print(f"\n📊 Running comprehensive backtest for {args.symbol} over {args.days} days...")
        print("This may take several minutes depending on data availability and timeframes...")
        
        start_time = datetime.now()
        results = engine.run_comprehensive_backtest(args.symbol, args.days)
        end_time = datetime.now()
        
        if not results:
            print("❌ Backtest failed to produce results")
            sys.exit(1)
        
        # Calculate execution time
        execution_time = end_time - start_time
        print(f"\n✅ Backtest completed in {execution_time.total_seconds():.1f} seconds")
        
        # Print comprehensive report
        engine.print_backtest_report(results)
        
        # Additional analysis
        print("\n🔍 DETAILED ANALYSIS")
        print("=" * 60)
        
        # Strategy performance ranking
        strategy_performance = []
        for strategy_name, result in results.items():
            if strategy_name in ['portfolio', 'correlations']:
                continue
            
            if 'performance' in result:
                perf = result['performance']
                strategy_performance.append({
                    'name': result['strategy'],
                    'timeframe': result['timeframe'],
                    'win_rate': perf['win_rate'],
                    'total_return': perf['total_return_pct'],
                    'sharpe_ratio': perf['sharpe_ratio'],
                    'max_drawdown': perf['max_drawdown_pct'],
                    'trades': perf['total_trades']
                })
        
        # Sort by total return
        strategy_performance.sort(key=lambda x: x['total_return'], reverse=True)
        
        print("🏆 STRATEGY PERFORMANCE RANKING (by Total Return):")
        for i, strategy in enumerate(strategy_performance, 1):
            print(f"{i}. {strategy['name']} ({strategy['timeframe']})")
            print(f"   Return: {strategy['total_return']:+.2f}% | Win Rate: {strategy['win_rate']:.1f}% | "
                  f"Sharpe: {strategy['sharpe_ratio']:.2f} | Drawdown: {strategy['max_drawdown']:.2f}% | "
                  f"Trades: {strategy['trades']}")
        
        # Risk analysis
        print(f"\n⚠️  RISK ANALYSIS:")
        print(f"Highest Win Rate: {max(s['win_rate'] for s in strategy_performance):.1f}%")
        print(f"Lowest Max Drawdown: {min(s['max_drawdown'] for s in strategy_performance):.2f}%")
        print(f"Best Sharpe Ratio: {max(s['sharpe_ratio'] for s in strategy_performance):.2f}")
        
        # Portfolio insights
        if 'portfolio' in results:
            portfolio = results['portfolio']
            print(f"\n💼 PORTFOLIO INSIGHTS:")
            print(f"Combined Return: {portfolio['total_return_pct']:+.2f}%")
            
            # Compare with individual strategies
            individual_returns = [s['total_return'] for s in strategy_performance]
            avg_individual_return = sum(individual_returns) / len(individual_returns)
            print(f"Average Individual Strategy Return: {avg_individual_return:+.2f}%")
            
            if portfolio['total_return_pct'] > avg_individual_return:
                print("✅ Portfolio outperforms average individual strategy (diversification benefit)")
            else:
                print("⚠️  Portfolio underperforms average individual strategy (correlation penalty)")
        
        # Correlation insights
        if 'correlations' in results:
            correlations = results['correlations']
            if correlations:
                print(f"\n🔗 DIVERSIFICATION INSIGHTS:")
                avg_correlation = sum(correlations.values()) / len(correlations)
                print(f"Average Strategy Correlation: {avg_correlation:.3f}")
                
                if avg_correlation < 0.3:
                    print("✅ Excellent diversification (low correlations)")
                elif avg_correlation < 0.6:
                    print("✅ Good diversification (moderate correlations)")
                else:
                    print("⚠️  Limited diversification (high correlations)")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        # Best performing strategy
        best_strategy = strategy_performance[0]
        print(f"1. Primary Focus: {best_strategy['name']} - Best overall performance")
        
        # Most consistent strategy (lowest drawdown)
        most_consistent = min(strategy_performance, key=lambda x: x['max_drawdown'])
        if most_consistent != best_strategy:
            print(f"2. Risk Management: {most_consistent['name']} - Lowest drawdown")
        
        # Highest win rate strategy
        highest_win_rate = max(strategy_performance, key=lambda x: x['win_rate'])
        if highest_win_rate != best_strategy:
            print(f"3. Consistency: {highest_win_rate['name']} - Highest win rate")
        
        # Capital allocation suggestions
        print(f"\n💰 CAPITAL ALLOCATION SUGGESTIONS:")
        print("Current allocation is risk-weighted:")
        for strategy, allocation in CAPITAL_ALLOCATION.items():
            strategy_display = strategy.replace('_', ' ').title()
            print(f"  {strategy_display}: {allocation*100:.0f}%")
        
        print(f"\n📈 NEXT STEPS:")
        print("1. Review individual trade details in the results")
        print("2. Analyze equity curves for drawdown patterns")
        print("3. Consider parameter optimization for underperforming strategies")
        print("4. Test with different time periods for robustness")
        print("5. Implement live trading with proper risk management")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Backtest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during backtesting: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        engine.cleanup()
        print("✅ Cleanup completed")


if __name__ == "__main__":
    main()
