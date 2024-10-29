import React from 'react';
import styles from './Footer.module.css';

const Footer: React.FC = () => {
    return (
        <footer className={styles.footer}>
            <p>© 2024 Crypto Arbitrage Bot. All Rights Reserved.</p>
        </footer>
    );
};

export default Footer;
