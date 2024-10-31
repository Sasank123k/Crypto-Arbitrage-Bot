import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/authcontext';
import Header from './components/header/header';
import Footer from './components/footer/footer';
import Home from './pages/home/home';
import Login from './pages/login/login';
import Signup from './pages/signup/signup';
import Dashboard from './pages/dashboard/dashboard';
import TradeHistory from './pages/tradehistory/tradehistory';
import AccountSettings from './pages/accountsettings/accountsettings';
import BacktestingPage from './pages/backtestingpage/backtestingpage';
import ProtectedRoute from './context/protectedroute';




import styles from './App.module.css';

const App: React.FC = () => {
    return (
        <Router>
            <AuthProvider>
            <div className={styles.appContainer}>
                <Header />
                <main className={styles.mainContent}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                        <Route
                        path="/dashboard"
                        element={<ProtectedRoute><Dashboard /></ProtectedRoute>}/>
                        <Route path="/trade-history" element={<TradeHistory/>} />
                        <Route path="/account-settings" element={<AccountSettings/>} />
                        <Route path="/backtesting" element={<BacktestingPage />} />

                    </Routes>
                </main>
                <Footer />
            </div>
        </AuthProvider>
        </Router>

    );
};

export default App;
