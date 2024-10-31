import React, { useState } from 'react';
import axios from 'axios';
import styles from './login.module.css';
import { useAuth } from '../../context/authcontext';
import { FaEnvelope, FaLock } from 'react-icons/fa'; // Importing icons for better UI

const Login: React.FC = () => {
    const { login } = useAuth(); // Access login function from AuthContext
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [message, setMessage] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false); // State to handle loading

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true); // Start loading
        setMessage(''); // Clear previous messages
        try {
            const response = await axios.post('http://localhost:5000/api/login', {
                email,
                password,
            });

            setMessage(response.data.message);

            if (response.data.token) {
                // Use login function from AuthContext and pass the token
                login(response.data.token);
            } else {
                setMessage("Login failed. No token received.");
            }
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                if (error.response && error.response.data) {
                    setMessage(error.response.data.message);
                } else {
                    setMessage("An error occurred. Please try again.");
                }
            } else {
                setMessage("An unexpected error occurred.");
            }
        } finally {
            setLoading(false); // End loading
        }
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
                {message && <p className={styles.message}>{message}</p>}
            </div>
        </div>
    );
};

export default Login;
