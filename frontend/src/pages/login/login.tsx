// src/pages/login/login.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for navigation
import styles from './login.module.css';
import { FaEnvelope, FaLock } from 'react-icons/fa'; // Importing icons for better UI

const Login: React.FC = () => {
    const navigate = useNavigate(); // Initialize navigation
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false); // State to handle loading

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true); // Start loading

        // Bypass authentication: directly navigate to Dashboard
        navigate('/dashboard');
    };

    return (
        <div className={styles.wrapper}>
            <div className={styles.card}>
                <h2 className={styles.title}>Login</h2>
                <form onSubmit={handleLogin} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <FaEnvelope className={styles.icon} />
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className={styles.input}
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <FaLock className={styles.icon} />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className={styles.input}
                        />
                    </div>
                    <button type="submit" className={styles.button} disabled={loading}>
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
