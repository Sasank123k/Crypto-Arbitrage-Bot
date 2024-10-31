import React from 'react';
import styles from './Home.module.css';

const Home: React.FC = () => {
    return (
        <div className={styles.container}>
            {/* Header Section */}
            <section className={styles.headerSection}>
                <div className={styles.headerContent}>
                    <h1>Trade Smarter with CryptoBot</h1>
                    <p>Leverage the power of AI and smart algorithms to capture arbitrage opportunities across global crypto exchanges.</p>
                    <button className={styles.getStartedButton}>Get Started</button>
                </div>
            </section>

            {/* Features Section */}
            <section className={styles.featuresSection}>
                <div className={styles.featureCard}>
                    <h3>Guaranteed Profits</h3>
                    <p>Our bot continuously scans for profitable trades, ensuring maximum return on each opportunity.</p>
                </div>
                <div className={styles.featureCard}>
                    <h3>Real-Time Analysis</h3>
                    <p>Stay ahead of the market with real-time data analysis from multiple exchanges.</p>
                </div>
                <div className={styles.featureCard}>
                    <h3>24/7 Support</h3>
                    <p>Get dedicated support and maximize your trading experience with expert guidance.</p>
                </div>
            </section>

            {/* Plans Section */}
            <section className={styles.plansSection}>
                <h2>Choose Your Plan</h2>
                <div className={styles.planCards}>
                    <div className={`${styles.planCard} ${styles.popularPlan}`}>
                        <h3>Pro Plan</h3>
                        <p>For advanced traders looking for maximum performance and detailed analysis.</p>
                        <ul>
                            <li>Up to 95% Profit Share</li>
                            <li>24/7 Monitoring</li>
                            <li>Real-time Data</li>
                            <li>No Limitations</li>
                        </ul>
                        <button className={styles.planButton}>Start Pro Plan</button>
                    </div>
                    <div className={styles.planCard}>
                        <h3>Starter Plan</h3>
                        <p>Perfect for beginners who are just entering the crypto trading space.</p>
                        <ul>
                            <li>Up to 75% Profit Share</li>
                            <li>Limited Monitoring</li>
                            <li>Basic Data Analysis</li>
                            <li>Supports Popular Coins</li>
                        </ul>
                        <button className={styles.planButton}>Start Starter Plan</button>
                    </div>
                    <div className={styles.planCard}>
                        <h3>Enterprise Plan</h3>
                        <p>Custom solutions for large trading firms and experienced traders.</p>
                        <ul>
                            <li>Tailored Profit Sharing</li>
                            <li>Dedicated Monitoring</li>
                            <li>Advanced Analytics</li>
                            <li>Supports Multi-Exchanges</li>
                        </ul>
                        <button className={styles.planButton}>Contact Us</button>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Home;
