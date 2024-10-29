import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import styles from './login.module.css';

const Login: React.FC = () => {
    const navigate = useNavigate(); // Initialize navigate

    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [message, setMessage] = useState<string>('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/api/login', {
                email,
                password,
            });

            // If your backend returns a token, store it (e.g., in localStorage)
            // localStorage.setItem('token', response.data.token);

            setMessage(response.data.message);

            // Redirect to the dashboard after successful login
            navigate('/dashboard');
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
        }
    };

    return (
        <div className={styles.container}>
            <h2>Login</h2>
            <form onSubmit={handleLogin} className={styles.form}>
                <label>Email:</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <label>Password:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Login</button>
            </form>
            <p>{message}</p>
        </div>
    );
};

export default Login;
