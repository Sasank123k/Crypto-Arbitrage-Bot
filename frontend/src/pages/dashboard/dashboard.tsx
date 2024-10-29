import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './dashboard.module.css';

const Dashboard: React.FC = () => {
    const [username, setUsername] = useState<string>('User');
    const [botStatus, setBotStatus] = useState<boolean>(false);
    const [profitLossData, setProfitLossData] = useState<number[]>([]);
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

        // Fetch initial data
        fetchUserData();
        fetchBotStatus();
        fetchProfitLossData();
        fetchArbitrageOpportunities();
        fetchMarketData();
    }, []);

    const fetchBotStatus = async () => {
        // Fetch bot status from the backend
        try {
            const response = await axios.get('http://localhost:5000/api/botstatus');
            setBotStatus(response.data.isActive);
        } catch (error) {
            console.error('Error fetching bot status:', error);
        }
    };

    const fetchProfitLossData = async () => {
        // Fetch profit/loss data for the graph
        try {
            const response = await axios.get('http://localhost:5000/api/profitloss');
            setProfitLossData(response.data);
        } catch (error) {
            console.error('Error fetching profit/loss data:', error);
        }
    };

    const fetchArbitrageOpportunities = async () => {
        // Fetch recent arbitrage opportunities
        try {
            const response = await axios.get('http://localhost:5000/api/arbitrageopportunities');
            setArbitrageOpportunities(response.data);
        } catch (error) {
            console.error('Error fetching arbitrage opportunities:', error);
        }
    };

    const fetchMarketData = async () => {
        // Fetch real-time market data
        try {
            const response = await axios.get('http://localhost:5000/api/marketdata');
            setMarketData(response.data);
        } catch (error) {
            console.error('Error fetching market data:', error);
        }
    };

    const toggleBotStatus = async () => {
        // Start or stop the arbitrage bot
        try {
            const response = await axios.post('http://localhost:5000/api/togglebot', {
                isActive: !botStatus,
            });
            setBotStatus(response.data.isActive);
        } catch (error) {
            console.error('Error toggling bot status:', error);
        }
    };

    return (
        <div className={styles.dashboard}>
            <h1>Welcome, {username}!</h1>
            <div className={styles.navigation}>
                <button onClick={toggleBotStatus} className={styles.navButton}>
                    {botStatus ? 'Stop Arbitrage Bot' : 'Start Arbitrage Bot'}
                </button>
                <button className={styles.navButton}>Trade History</button>
                <button className={styles.navButton}>Account Settings</button>
            </div>
            <div className={styles.mainContent}>
                <div className={styles.section}>
                    <h2>Arbitrage Opportunities</h2>
                    {arbitrageOpportunities.length > 0 ? (
                        <ul className={styles.opportunitiesList}>
                            {arbitrageOpportunities.map((opportunity, index) => (
                                <li key={index} className={styles.opportunityItem}>
                                    <strong>{opportunity.asset}</strong>: Buy on <strong>{opportunity.buyExchange}</strong> at <strong>{opportunity.buyPrice}</strong>, 
                                    Sell on <strong>{opportunity.sellExchange}</strong> at <strong>{opportunity.sellPrice}</strong>, Profit: <strong>{opportunity.profit}%</strong>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No arbitrage opportunities available at the moment.</p>
                    )}
                </div>
                <div className={styles.section}>
                    <h2>Profit/Loss Graph</h2>
                    {/* Integrate a chart library like Chart.js or Recharts here */}
                    <p>[Graph displaying cumulative profit/loss]</p>
                </div>
                <div className={styles.section}>
                    <h2>Real-Time Market Data</h2>
                    {marketData.length > 0 ? (
                        <table className={styles.marketTable}>
                            <thead>
                                <tr>
                                    <th>Asset</th>
                                    <th>Exchange</th>
                                    <th>Price</th>
                                </tr>
                            </thead>
                            <tbody>
                                {marketData.map((data, index) => (
                                    <tr key={index}>
                                        <td>{data.asset}</td>
                                        <td>{data.exchange}</td>
                                        <td>{data.price}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <p>Loading market data...</p>
                    )}
                </div>
                <div className={styles.section}>
                    <h2>Bot Status</h2>
                    <p>
                        The arbitrage bot is currently:{' '}
                        <strong className={botStatus ? styles.activeText : styles.inactiveText}>
                            {botStatus ? 'Active' : 'Inactive'}
                        </strong>
                    </p>
                    <button
                        onClick={toggleBotStatus}
                        className={`${styles.botButton} ${
                            botStatus ? styles.stopButton : styles.startButton
                        }`}
                    >
                        {botStatus ? 'Stop Bot' : 'Start Bot'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
