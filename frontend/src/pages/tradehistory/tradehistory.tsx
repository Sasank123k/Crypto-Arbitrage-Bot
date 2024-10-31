// TradeHistory.tsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './tradeHistory.module.css';

const TradeHistory: React.FC = () => {
    const [tradeHistory, setTradeHistory] = useState<any[]>([]);

    useEffect(() => {
        const fetchTradeHistory = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/trade-history');
                setTradeHistory(response.data);
            } catch (error) {
                console.error('Error fetching trade history:', error);
            }
        };

        fetchTradeHistory();
    }, []);

    return (
        <div className={styles.tradeHistory}>
            <h2>Trade History</h2>
            {tradeHistory.length > 0 ? (
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
                                <th>Profit</th>
                                <th>Profit %</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tradeHistory.map((trade, index) => (
                                <tr key={index}>
                                    <td>{new Date(trade.timestamp).toLocaleString()}</td>
                                    <td>{trade.asset}</td>
                                    <td>{trade.buy_exchange}</td>
                                    <td>{trade.sell_exchange}</td>
                                    <td>${trade.buy_price}</td>
                                    <td>${trade.sell_price}</td>
                                    <td>${trade.profit}</td>
                                    <td>{trade.profit_percentage}%</td>
                                </tr>
                            ))}
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
