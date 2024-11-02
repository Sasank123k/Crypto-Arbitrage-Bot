// src/pages/tradehistory/tradeHistory.tsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './tradeHistory.module.css';
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
            {error && <p className={styles.error}>{error}</p>}
            {isLoading ? (
                <p>Loading trade history...</p>
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
                                <th>Buy Fee</th>
                                <th>Sell Fee</th>
                                <th>Withdrawal Fee</th>
                                <th>Buy Slippage</th>
                                <th>Sell Slippage</th>
                                <th>Latency (s)</th>
                                <th>Est. Price Change</th>
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
                                        
                                        {/* Buy Fee */}
                                        <td>
                                            {trade.buy_fee != null
                                                ? `$${trade.buy_fee.toFixed(4)}`
                                                : 'N/A'}
                                        </td>
                                        
                                        {/* Sell Fee */}
                                        <td>
                                            {trade.sell_fee != null
                                                ? `$${trade.sell_fee.toFixed(4)}`
                                                : 'N/A'}
                                        </td>
                                        
                                        {/* Withdrawal Fee */}
                                        <td>
                                            {trade.withdrawal_fee != null
                                                ? `$${trade.withdrawal_fee.toFixed(4)}`
                                                : 'N/A'}
                                        </td>
                                        
                                        {/* Buy Slippage */}
                                        <td>
                                            {trade.buy_slippage != null
                                                ? `${(trade.buy_slippage * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        
                                        {/* Sell Slippage */}
                                        <td>
                                            {trade.sell_slippage != null
                                                ? `${(trade.sell_slippage * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                        
                                        {/* Latency */}
                                        <td>
                                            {trade.latency != null
                                                ? trade.latency.toFixed(2)
                                                : 'N/A'}
                                        </td>
                                        
                                        {/* Estimated Price Change */}
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
                                                ? `${(trade.profit_percentage * 100).toFixed(2)}%`
                                                : 'N/A'}
                                        </td>
                                    </tr>
                                )
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
