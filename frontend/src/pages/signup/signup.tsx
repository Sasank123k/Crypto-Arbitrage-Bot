import React, { useState } from 'react';
import axios from 'axios';
import styles from './signup.module.css';

const Signup: React.FC = () => {
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [message, setMessage] = useState<string>('');

    const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/api/signup', {
                email,
                password,
            });
            setMessage(response.data.message); // Expecting "User created successfully"
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
            <h2>Signup</h2>
            <form onSubmit={handleSignup} className={styles.form}>
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
                <button type="submit">Signup</button>
            </form>
            <p>{message}</p>
        </div>
    );
};

export default Signup;
