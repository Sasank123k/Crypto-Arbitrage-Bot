// AccountSettings.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './accountSettings.module.css';

const AccountSettings: React.FC = () => {
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/userdata');
                setEmail(response.data.email);
            } catch (error) {
                console.error('Error fetching user data:', error);
            }
        };

        fetchUserData();
    }, []);

    const handleSaveChanges = async () => {
        try {
            await axios.post('http://localhost:5000/api/update-account', {
                email,
                password,
            });
            alert('Account updated successfully!');
        } catch (error) {
            console.error('Error updating account:', error);
            alert('Failed to update account.');
        }
    };

    return (
        <div className={styles.accountSettings}>
            <h2>Account Settings</h2>
            <form onSubmit={(e) => e.preventDefault()} className={styles.form}>
                <div className={styles.formGroup}>
                    <label htmlFor="email">Email:</label>
                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="password">New Password:</label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Leave blank to keep current password"
                    />
                </div>
                <button type="submit" onClick={handleSaveChanges} className={styles.saveButton}>
                    Save Changes
                </button>
            </form>
        </div>
    );
};

export default AccountSettings;
