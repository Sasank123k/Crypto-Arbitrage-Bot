import React, { useState } from 'react';
import axios from 'axios';
import styles from './login.module.css';
import { useAuth } from '../../context/authcontext';

const Login: React.FC = () => {
    const { login } = useAuth(); // Access login function from AuthContext
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
