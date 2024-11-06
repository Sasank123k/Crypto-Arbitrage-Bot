// src/pages/tradehistory/tradeHistory.tsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './tradeHistory.module.css';
import { Link } from 'react-router-dom'; // Added for navigation
import { Trade } from '../../interfaces'; // Ensure correct path

const TradeHistory: React.FC = () => {
    const [tradeHistory, setTradeHistory] = useState<Trade[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTradeHistory = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get<Trade[]>('http://localhost:5000/api/trade-history');
                console.log('Fetched Trade History:', response.data); // Debugging
                setTradeHistory(response.data);
                setError(null);
            } catch (error) {
                console.error('Error fetching trade history:', error);
                setError('Failed to fetch trade history.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchTradeHistory();
    }, []);

    return (
        <div className={styles.tradeHistory}>
            <h2>Trade History</h2>

            {/* Navigation Section */}
            <div className={styles.navigation}>
                <Link to="/dashboard" className={styles.navButton}>
                    Dashboard
                </Link>
                <Link to="/backtesting" className={styles.navButton}>
                    Backtesting
                </Link>
                <Link to="/account-settings" className={styles.navButton}>
                    Account Settings
                </Link>
                {/* Add more navigation buttons if needed */}
            </div>

            {error && <p className={styles.error}>{error}</p>}
            {isLoading ? (
                <p className={styles.isLoading}>Loading trade history...</p>
            ) : tradeHistory.length > 0 ? (
                <div className={styles.tableContainer}>
                    <table className={styles.tradeTable}>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Asset</th>
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
                            {tradeHistory.map((trade) => {
                                console.log('Processing Trade:', trade); // Debugging
                                return (
                                    <tr key={trade.id}>
                                        {/* Date */}
                                        <td>
                                            {trade.timestamp
                                                ? new Date(trade.timestamp).toLocaleString()
                                                : 'N/A'}
                                        </td>
                                        {/* Asset */}
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
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            ) : (
                <p>No trade history available.</p>
            )}
        </div>
    );

};
    export default TradeHistory;
