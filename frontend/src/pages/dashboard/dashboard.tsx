// src/pages/dashboard/dashboard.tsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import styles from './dashboard.module.css';
import { Link } from 'react-router-dom';
import { ArbitrageOpportunity, MarketData, ProfitLossSummary } from '../../interfaces'; // Ensure correct path

const Dashboard: React.FC = () => {
    const [botStatus, setBotStatus] = useState<string>('inactive');
    const [profitLossSummary, setProfitLossSummary] = useState<ProfitLossSummary>({
        total_gross_profit: 0,
        total_net_profit: 0,
    });
    const [arbitrageOpportunities, setArbitrageOpportunities] = useState<ArbitrageOpportunity[]>([]);
    const [marketData, setMarketData] = useState<MarketData[]>([]);
    const [error, setError] = useState<string | null>(null); // State to handle errors

    useEffect(() => {
        fetchBotStatus();
        fetchProfitLossSummary();
        fetchArbitrageOpportunities();
        fetchMarketData();

        // Set up intervals for continuous data fetching
        const botStatusInterval = setInterval(fetchBotStatus, 20000); // Every 20 seconds
        const profitInterval = setInterval(fetchProfitLossSummary, 20000); // Every 20 seconds
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
            const response = await axios.get<{ status: string }>('http://localhost:5000/api/bot-status');
            setBotStatus(response.data.status);
            setError(null);
        } catch (error) {
            console.error('Error fetching bot status:', error);
            setError('Failed to fetch bot status.');
        }
    };

    const fetchProfitLossSummary = async () => {
        try {
            const response = await axios.get<ProfitLossSummary>('http://localhost:5000/api/profit-loss-summary');
            setProfitLossSummary(response.data);
            setError(null);
        } catch (error) {
            console.error('Error fetching profit and loss summary:', error);
            setError('Failed to fetch profit and loss summary.');
        }
    };

    const fetchArbitrageOpportunities = async () => {
        try {
            const response = await axios.get<ArbitrageOpportunity[]>('http://localhost:5000/api/arbitrage-opportunities');
            setArbitrageOpportunities(response.data);
            setError(null);
        } catch (error) {
            console.error('Error fetching arbitrage opportunities:', error);
            setError('Failed to fetch arbitrage opportunities.');
        }
    };

    const fetchMarketData = async () => {
        try {
            const response = await axios.get<MarketData[]>('http://localhost:5000/api/market-data');
            setMarketData(response.data);
            setError(null);
        } catch (error) {
            console.error('Error fetching market data:', error);
            setError('Failed to fetch market data.');
        }
    };

    const toggleBotStatus = async () => {
        try {
            const response = await axios.post<{ isActive: boolean; message: string }>('http://localhost:5000/api/togglebot', {
                isActive: botStatus !== 'active',
            });
            setBotStatus(response.data.isActive ? 'active' : 'inactive');
            setError(null);
            // Optionally, display a success message
        } catch (error) {
            console.error('Error toggling bot status:', error);
            setError('Failed to toggle bot status.');
        }
    };

    // Organize market data by currency
    const groupedMarketData = marketData.reduce((acc: { [key: string]: MarketData[] }, data: MarketData) => {
        const { symbol } = data;
        if (!acc[symbol]) {
            acc[symbol] = [];
        }
        acc[symbol].push(data);
        return acc;
    }, {});

    return (
        <div className={styles.dashboard}>
            <h1>Welcome to the Dashboard!</h1>

            {/* Navigation Section */}
            <div className={styles.navigation}>
                <button
                    onClick={toggleBotStatus}
                    className={styles.navButton}
                    aria-label={botStatus === 'active' ? 'Stop the arbitrage bot' : 'Start the arbitrage bot'}
                >
                    {botStatus === 'active' ? 'Stop Arbitrage Bot' : 'Start Arbitrage Bot'}
                </button>
                <Link to="/trade-history" className={styles.navButton}>
                    Trade History
                </Link>
                <Link to="/account-settings" className={styles.navButton}>
                    Account Settings
                </Link>
                <Link to="/backtesting" className={styles.navButton}>
                    Backtesting
                </Link>
                {/* Future Feature Link (optional) */}
                {/* <Link to="/future-feature" className={styles.navButton}>
                    Future Feature
                </Link> */}
            </div>

            {/* Display Error Message if Any */}
            {error && <p className={styles.error}>{error}</p>}

            <div className={styles.mainContent}>
                {/* Bot Status Section */}
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
                        aria-label={botStatus === 'active' ? 'Stop the arbitrage bot' : 'Start the arbitrage bot'}
                    >
                        {botStatus === 'active' ? 'Stop Bot' : 'Start Bot'}
                    </button>
                </div>

                {/* Profit Summary Section */}
                <div className={styles.section}>
                    <h2>Profit Summary</h2>
                    <p>Total Gross Profit: ${profitLossSummary.total_gross_profit.toFixed(2)}</p>
                    <p>Total Net Profit: ${profitLossSummary.total_net_profit.toFixed(2)}</p>
                    {/* Removed Total Loss as it's same as Net Profit */}
                </div>

                {/* Arbitrage Opportunities Section */}
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
                                        <th>Gross Profit</th> {/* Added Gross Profit Column */}
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
                                    {arbitrageOpportunities.map((opportunity, index) => (
                                        <tr key={index}>
                                            {/* Timestamp */}
                                            <td>
                                                {opportunity.timestamp
                                                    ? new Date(opportunity.timestamp).toLocaleString()
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Currency */}
                                            <td>{opportunity.currency ?? 'N/A'}</td>
                                            
                                            {/* Buy Exchange */}
                                            <td>{opportunity.exchange_buy ?? 'N/A'}</td>
                                            
                                            {/* Buy Price */}
                                            <td>
                                                {opportunity.buy_price != null
                                                    ? `$${opportunity.buy_price.toFixed(2)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Sell Exchange */}
                                            <td>{opportunity.exchange_sell ?? 'N/A'}</td>
                                            
                                            {/* Sell Price */}
                                            <td>
                                                {opportunity.sell_price != null
                                                    ? `$${opportunity.sell_price.toFixed(2)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Gross Profit */}
                                            <td>
                                                {opportunity.gross_profit != null
                                                    ? `$${opportunity.gross_profit.toFixed(2)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Buy Fee */}
                                            <td>
                                                {opportunity.buy_fee != null
                                                    ? `$${opportunity.buy_fee.toFixed(4)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Sell Fee */}
                                            <td>
                                                {opportunity.sell_fee != null
                                                    ? `$${opportunity.sell_fee.toFixed(4)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Withdrawal Fee */}
                                            <td>
                                                {opportunity.withdrawal_fee != null
                                                    ? `$${opportunity.withdrawal_fee.toFixed(4)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Buy Slippage */}
                                            <td>
                                                {opportunity.buy_slippage != null
                                                    ? `${(opportunity.buy_slippage * 100).toFixed(2)}%`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Sell Slippage */}
                                            <td>
                                                {opportunity.sell_slippage != null
                                                    ? `${(opportunity.sell_slippage * 100).toFixed(2)}%`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Latency */}
                                            <td>
                                                {opportunity.latency != null
                                                    ? opportunity.latency.toFixed(2)
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Estimated Price Change */}
                                            <td>
                                                {opportunity.estimated_price_change != null
                                                    ? `$${opportunity.estimated_price_change.toFixed(2)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Net Profit */}
                                            <td>
                                                {opportunity.net_profit != null
                                                    ? `$${opportunity.net_profit.toFixed(2)}`
                                                    : 'N/A'}
                                            </td>
                                            
                                            {/* Profit % */}
                                            <td>
                                                {opportunity.net_profit != null && opportunity.gross_profit !== 0
                                                    ? `${((opportunity.net_profit / opportunity.gross_profit) * 100).toFixed(2)}%`
                                                    : 'N/A'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p>No arbitrage opportunities available at the moment.</p>
                    )}
                </div>

                {/* Real-Time Market Data Section */}
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
                                        {groupedMarketData[symbol].map((data: MarketData, index: number) => (
                                            <tr key={index}>
                                                <td>{data.exchange ?? 'N/A'}</td>
                                                <td>
                                                    {data.price != null
                                                        ? `$${data.price.toFixed(2)}`
                                                        : 'N/A'}
                                                </td>
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
