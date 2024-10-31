// BacktestingPage.tsx
import React, { useState } from 'react';
import axios from 'axios';
import styles from './backtestingPage.module.css';

const BacktestingPage: React.FC = () => {
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
    const [backtestResult, setBacktestResult] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);

    const symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']; // Add more symbols as needed

    const handleBacktest = async () => {
        setIsLoading(true);
        try {
            const response = await axios.post('http://localhost:5000/api/backtest', {
                start_date: startDate,
                end_date: endDate,
                symbol: selectedSymbol,
            });
            setBacktestResult(response.data);
        } catch (error) {
            console.error('Error running backtest:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.backtestingPage}>
            <h2>Backtesting</h2>
            <form onSubmit={(e) => e.preventDefault()} className={styles.form}>
                <div className={styles.formGroup}>
                    <label htmlFor="startDate">Start Date:</label>
                    <input
                        id="startDate"
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        required
                    />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="endDate">End Date:</label>
                    <input
                        id="endDate"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        required
                    />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="symbol">Cryptocurrency:</label>
                    <select
                        id="symbol"
                        value={selectedSymbol}
                        onChange={(e) => setSelectedSymbol(e.target.value)}
                        required
                    >
                        {symbols.map((symbol) => (
                            <option key={symbol} value={symbol}>
                                {symbol}
                            </option>
                        ))}
                    </select>
                </div>
                <button
                    onClick={handleBacktest}
                    disabled={!startDate || !endDate || isLoading}
                    className={styles.runButton}
                >
                    {isLoading ? 'Running...' : 'Run Backtest'}
                </button>
            </form>
            {backtestResult && (
                <div className={styles.results}>
                    <h3>Backtest Results</h3>
                    <p>Total Profit: ${backtestResult.total_profit.toFixed(2)}</p>
                    <div className={styles.tableContainer}>
                        <table className={styles.resultsTable}>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Buy Exchange</th>
                                    <th>Sell Exchange</th>
                                    <th>Profit</th>
                                </tr>
                            </thead>
                            <tbody>
                                {backtestResult.trades.map((trade: any, index: number) => (
                                    <tr key={index}>
                                        <td>{new Date(trade.timestamp).toLocaleDateString()}</td>
                                        <td>{trade.buy_exchange}</td>
                                        <td>{trade.sell_exchange}</td>
                                        <td>${trade.profit.toFixed(2)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BacktestingPage;
