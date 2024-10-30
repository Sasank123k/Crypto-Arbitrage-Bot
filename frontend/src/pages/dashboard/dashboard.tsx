import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './dashboard.module.css';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
    const [username, setUsername] = useState<string>('User');
    const [botStatus, setBotStatus] = useState<string>('inactive');
    const [profitLossData, setProfitLossData] = useState<any>({});
    const [arbitrageOpportunities, setArbitrageOpportunities] = useState<any[]>([]);
    const [marketData, setMarketData] = useState<any>({});

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
        fetchProfitLossData();
        fetchArbitrageOpportunities();
        fetchMarketData();

        // Set up intervals for continuous data fetching
        const botStatusInterval = setInterval(fetchBotStatus, 20000); // Every 5 seconds
        const profitLossInterval = setInterval(fetchProfitLossData, 20000); // Every 10 seconds
        const opportunitiesInterval = setInterval(fetchArbitrageOpportunities, 20000); // Every 5 seconds
        const marketDataInterval = setInterval(fetchMarketData, 20000); // Every 5 seconds

        return () => {
            clearInterval(botStatusInterval);
            clearInterval(profitLossInterval);
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

    const fetchProfitLossData = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/profit-loss-summary');
            setProfitLossData(response.data);
        } catch (error) {
            console.error('Error fetching profit/loss data:', error);
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

    return (
        <div className={styles.dashboard}>
            <h1>Welcome, {username}!</h1>
            
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
                    <h2>Profit/Loss Summary</h2>
                    <p>Total Profit: ${profitLossData.total_profit}</p>
                    <p>Total Loss: ${profitLossData.total_loss}</p>
                </div>
                <div className={styles.section}>
                    <h2>Arbitrage Opportunities</h2>
                    {arbitrageOpportunities.length > 0 ? (
                        <ul className={styles.opportunitiesList}>
                            {arbitrageOpportunities.map((opportunity, index) => (
                                <li key={index} className={styles.opportunityItem}>
                                    {opportunity.currency}: Buy on <strong>{opportunity.exchange_buy || opportunity.exchange1}</strong> at{' '}
                                    <strong>${opportunity.buy_price || opportunity.buyPrice}</strong>, Sell on{' '}
                                    <strong>{opportunity.exchange_sell || opportunity.exchange2}</strong> at{' '}
                                    <strong>${opportunity.sell_price || opportunity.sellPrice}</strong>, Profit: <strong>${opportunity.profit}</strong> ({opportunity.profit_percentage || opportunity.profitPercentage}%)
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No arbitrage opportunities available at the moment.</p>
                    )}
                </div>
                <div className={styles.section}>
                    <h2>Real-Time Market Data</h2>
                    {Object.keys(marketData).length > 0 ? (
                        <table className={styles.marketTable}>
                            <thead>
                                <tr>
                                    <th>Asset</th>
                                    <th>Exchange</th>
                                    <th>Price</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(marketData).map(([currency, data]: any, index) => (
                                    <tr key={index}>
                                        <td>{currency}</td>
                                        <td>{data.exchange}</td>
                                        <td>${data.price}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <p>Loading market data...</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
