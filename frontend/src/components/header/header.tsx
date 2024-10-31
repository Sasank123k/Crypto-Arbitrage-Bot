import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/authcontext';
import styles from './header.module.css';

const Header: React.FC = () => {
    const { isAuthenticated, logout } = useAuth();

    return (
        <header className={styles.header}>
            <div className={styles.logoContainer}>
                <img src="./src/assets/header_logo.png" alt="Crypto Arbitrage Bot Logo" className={styles.logoImage} />
                <h1 className={styles.logoText}>Crypto Arbitrage Bot</h1>
            </div>
            <nav>
                <ul className={styles.navList}>
                    <li><Link to="/">Home</Link></li>
                    <li><Link to="/models">Models</Link></li>
                    <li><Link to="/faq">FAQ</Link></li>
                    <li><Link to="/partner">Be a Partner</Link></li>
                    <li><Link to="/more">More</Link></li>
                </ul>
            </nav>
            <div className={styles.actions}>
                {isAuthenticated ? (
                    <>
                        <Link to="/dashboard" className={styles.actionButton}>Dashboard</Link>
                        <button className={styles.logoutButton} onClick={logout}>
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/login" className={styles.loginButton}>Log In</Link>
                        <Link to="/signup" className={styles.trialButton}>Free Trial</Link>
                    </>
                )}
                {/* <div className={styles.languageSelector}>
                    <img src="flag-icon.png" alt="Language" className={styles.flagIcon} />
                    <span>EN</span>
                </div> */}
            </div>
        </header>
    );
};

export default Header;
