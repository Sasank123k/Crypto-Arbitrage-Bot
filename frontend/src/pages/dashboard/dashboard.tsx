// Dashboard.tsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './dashboard.module.css';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
    const [username, setUsername] = useState<string>('User');
    const [botStatus, setBotStatus] = useState<string>('inactive');
    const [totalProfit, setTotalProfit] = useState<number>(0);
    const [arbitrageOpportunities, setArbitrageOpportunities] = useState<any[]>([]);
    const [marketData, setMarketData] = useState<any[]>([]);

    useEffect(() => {
        // Fetch user data
        const fetchUserData = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/userdata');
                setUsername(response.data.username);
            } catch (error) {
                console.error('Error fetching user data:', error);
            }
        };

        fetchUserData();
        fetchBotStatus();
        fetchProfitData();
        fetchArbitrageOpportunities();
        fetchMarketData();

        // Set up intervals for continuous data fetching
        const botStatusInterval = setInterval(fetchBotStatus, 20000); // Every 20 seconds
        const profitInterval = setInterval(fetchProfitData, 20000); // Every 20 seconds
        const opportunitiesInterval = setInterval(fetchArbitrageOpportunities, 20000); // Every 20 seconds
        const marketDataInterval = setInterval(fetchMarketData, 20000); // Every 20 seconds

        return () => {
            clearInterval(botStatusInterval);
            clearInterval(profitInterval);
            clearInterval(opportunitiesInterval);
            clearInterval(marketDataInterval);
        };
    }, []);

    const fetchBotStatus = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/bot-status');
            setBotStatus(response.data.status);
        } catch (error) {
            console.error('Error fetching bot status:', error);
        }
    };

    const fetchProfitData = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/profit-loss-summary');
            setTotalProfit(response.data.total_profit);
        } catch (error) {
            console.error('Error fetching profit data:', error);
        }
    };

    const fetchArbitrageOpportunities = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/arbitrage-opportunities');
            setArbitrageOpportunities(response.data);
        } catch (error) {
            console.error('Error fetching arbitrage opportunities:', error);
        }
    };

    const fetchMarketData = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/market-data');
                setMarketData(response.data);
            } catch (error) {
            console.error('Error fetching market data:', error);
        }
    };

    const toggleBotStatus = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/togglebot', {
                isActive: botStatus !== 'active',
            });
            setBotStatus(response.data.isActive ? 'active' : 'inactive');
        } catch (error) {
            console.error('Error toggling bot status:', error);
        }
    };

    // Organize market data by currency
    const groupedMarketData = marketData.reduce((acc: any, data: any) => {
        const { symbol, exchange, price } = data;
        if (!acc[symbol]) {
            acc[symbol] = [];
        }
        acc[symbol].push({ exchange, price });
        return acc;
    }, {});

    return (
        <div className={styles.dashboard}>
            <h1>Welcome, {username}!</h1>

            {/* Updated Navigation Section */}
            <div className={styles.navigation}>
                <button onClick={toggleBotStatus} className={styles.navButton}>
                    {botStatus === 'active' ? 'Stop Arbitrage Bot' : 'Start Arbitrage Bot'}
                </button>
                <Link to="/trade-history" className={styles.navButton}>
                    Trade History
                </Link>
                <Link to="/account-settings" className={styles.navButton}>
                    Account Settings
                </Link>
                {/* New Navigation Buttons */}
                <Link to="/backtesting" className={styles.navButton}>
                    Backtesting
                </Link>
                <Link to="/future-feature" className={styles.navButton}>
                    Future Feature
                </Link>
            </div>

            <div className={styles.mainContent}>
                <div className={styles.section}>
                    <h2>Bot Status</h2>
                    <p>
                        The arbitrage bot is currently:{' '}
                        <strong className={botStatus === 'active' ? styles.activeText : styles.inactiveText}>
                            {botStatus === 'active' ? 'Active' : 'Inactive'}
                        </strong>
                    </p>
                    <button
                        onClick={toggleBotStatus}
                        className={`${styles.botButton} ${
                            botStatus === 'active' ? styles.stopButton : styles.startButton
                        }`}
                    >
                        {botStatus === 'active' ? 'Stop Bot' : 'Start Bot'}
                    </button>
                </div>

                <div className={styles.section}>
                    <h2>Profit Summary</h2>
                    <p>Total Profit: ${totalProfit.toFixed(2)}</p>
                </div>

                <div className={styles.section}>
                    <h2>Arbitrage Opportunities</h2>
                    {arbitrageOpportunities.length > 0 ? (
                        <div className={styles.opportunitiesContainer}>
                            <table className={styles.opportunitiesTable}>
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>Currency</th>
                                        <th>Buy Exchange</th>
                                        <th>Buy Price</th>
                                        <th>Sell Exchange</th>
                                        <th>Sell Price</th>
                                        <th>Profit</th>
                                        <th>Profit %</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {arbitrageOpportunities.map((opportunity, index) => (
                                        <tr key={index}>
                                            <td>{new Date(opportunity.timestamp).toLocaleString()}</td>
                                            <td>{opportunity.currency}</td>
                                            <td>{opportunity.exchange_buy}</td>
                                            <td>${opportunity.buy_price}</td>
                                            <td>{opportunity.exchange_sell}</td>
                                            <td>${opportunity.sell_price}</td>
                                            <td>${opportunity.profit}</td>
                                            <td>{opportunity.profit_percentage}%</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p>No arbitrage opportunities available at the moment.</p>
                    )}
                </div>

                <div className={styles.section}>
                    <h2>Real-Time Market Data</h2>
                    {Object.keys(groupedMarketData).length > 0 ? (
                        Object.keys(groupedMarketData).map((symbol) => (
                            <div key={symbol} className={styles.marketDataSection}>
                                <h3>{symbol}</h3>
                                <table className={styles.marketTable}>
                                    <thead>
                                        <tr>
                                            <th>Exchange</th>
                                            <th>Price</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {groupedMarketData[symbol].map((data: any, index: number) => (
                                            <tr key={index}>
                                                <td>{data.exchange}</td>
                                                <td>${data.price}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ))
                    ) : (
                        <p>Loading market data...</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
