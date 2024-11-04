// src/pages/backtestingpage/backtestingPage.tsx

import React, { useState } from 'react';
import axios from 'axios';
import styles from './backtestingPage.module.css';
import { Link } from 'react-router-dom'; // Added for navigation
import { Trade, BacktestResult } from '../../interfaces'; // Ensure correct path

const BacktestingPage: React.FC = () => {
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
    const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const symbols = ['BTC/USDT', 'ETH/USDT']; // Removed 'LTC/USDT'

    const handleBacktest = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await axios.post<BacktestResult>('http://localhost:5000/api/backtest', {
                start_date: startDate,
                end_date: endDate,
                symbol: selectedSymbol,
            });
            console.log('Backtest Result:', response.data); // For debugging
            setBacktestResult(response.data);
        } catch (error) {
            console.error('Error running backtest:', error);
            setError('Failed to run backtest.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.backtestingPage}>
            <h2>Backtesting</h2>

            {/* Navigation Section */}
            <div className={styles.navigation}>
                <Link to="/dashboard" className={styles.navButton}>
                    Dashboard
                </Link>
                <Link to="/trade-history" className={styles.navButton}>
                    Trade History
                </Link>
                <Link to="/account-settings" className={styles.navButton}>
                    Account Settings
                </Link>
                {/* Add more navigation buttons if needed */}
            </div>

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
            {error && <p className={styles.error}>{error}</p>}
            {backtestResult && (
                <div className={styles.results}>
                    <h3>Backtest Results</h3>
                    <p>Total Gross Profit: ${backtestResult.total_profit.toFixed(2)}</p>
                    <div className={styles.tableContainer}>
                        <table className={styles.resultsTable}>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Currency</th>
                                    <th>Buy Exchange</th>
                                    <th>Sell Exchange</th>
                                    <th>Buy Price</th>
                                    <th>Sell Price</th>
                                    <th>Amount</th>
                                    <th>Gross Profit</th>
                                    <th>Gross Profit %</th>
                                    {/* Realistic Factors Columns */}
                                    <th>Buy Fee</th>
                                    <th>Sell Fee</th>
                                    <th>Withdrawal Fee</th>
                                    <th>Buy Slippage</th>
                                    <th>Sell Slippage</th>
                                    <th>Latency (s)</th>
                                    <th>Est. Price Change</th>
                                    {/* Moved Net Profit Columns to End */}
                                    <th>Net Profit</th>
                                    <th>Profit %</th>
                                </tr>
                            </thead>
                            <tbody>
                                {backtestResult.trades.map((trade: Trade, index: number) => (
                                    <tr key={index}>
                                        {/* Date */}
                                        <td>
                                            {trade.timestamp
                                                ? new Date(trade.timestamp).toLocaleDateString()
                                                : 'N/A'}
                                        </td>
                                        {/* Currency */}
                                        <td>{trade.asset ?? 'N/A'}</td>
                                        {/* Buy Exchange */}
                                        <td>{trade.buy_exchange ?? 'N/A'}</td>
                                        {/* Sell Exchange */}
                                        <td>{trade.sell_exchange ?? 'N/A'}</td>
                                        {/* Buy Price */}
                                        <td>
                                            {trade.buy_price != null
                                                ? `$${trade.buy_price.toFixed(2)}`
                                                : 'N/A'}
                                        </td>
                                        {/* Sell Price */}
                                        <td>
                                            {trade.sell_price != null
                                                ? `$${trade.sell_price.toFixed(2)}`
                                                : 'N/A'}
                                        </td>
                                        {/* Amount */}
                                        <td>
                                            {trade.amount != null
                                                ? trade.amount.toFixed(4)
                                                : 'N/A'}
                                        </td>
                                        {/* Gross Profit */}
                                        <td>
                                            {trade.gross_profit != null
                                                ? `$${trade.gross_profit.toFixed(2)}`
                                                : 'N/A'}
                                        </td>
                                        {/* Gross Profit % */}
                                        <td>
                                            {trade.gross_profit_percentage != null
                                                ? `${trade.gross_profit_percentage.toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        {/* Realistic Factors (for display only) */}
                                        <td>
                                            {trade.buy_fee != null
                                                ? `${(trade.buy_fee * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        <td>
                                            {trade.sell_fee != null
                                                ? `${(trade.sell_fee * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        <td>
                                            {trade.withdrawal_fee != null
                                                ? `${(trade.withdrawal_fee * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        <td>
                                            {trade.buy_slippage != null
                                                ? `${(trade.buy_slippage * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        <td>
                                            {trade.sell_slippage != null
                                                ? `${(trade.sell_slippage * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        <td>
                                            {trade.latency != null
                                                ? trade.latency.toFixed(2)
                                                : 'N/A'}
                                        </td>
                                        <td>
                                            {trade.estimated_price_change != null
                                                ? `$${trade.estimated_price_change.toFixed(2)}`
                                                : 'N/A'}
                                        </td>
                                        {/* Net Profit */}
                                        <td>
                                            {trade.profit != null
                                                ? `$${trade.profit.toFixed(2)}`
                                                : 'N/A'}
                                        </td>
                                        {/* Profit % */}
                                        <td>
                                            {trade.profit_percentage != null
                                                ? `${trade.profit_percentage.toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
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
