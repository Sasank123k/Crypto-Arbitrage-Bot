import React from 'react';
import styles from './Home.module.css';

const Home: React.FC = () => {
    return (
        <div className={styles.container}>
            <main className={styles.main}>
                <h2>Welcome to the Crypto Arbitrage Bot</h2>
                <p>Trade smarter by finding arbitrage opportunities across exchanges!</p>
            </main>
        </div>
    );
};

export default Home;
