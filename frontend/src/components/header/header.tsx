import React from 'react';
import styles from './header.module.css';

const Header: React.FC = () => {
    return (
        <header className={styles.header}>
            <div className={styles.logo}>
                Crypto Arbitrage Bot
            </div>
            <nav>
                <ul className={styles.navLinks}>
                    <li><a href="/login">Login</a></li>
                    <li><a href="/signup">Signup</a></li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;
