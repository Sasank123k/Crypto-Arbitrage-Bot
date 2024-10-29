import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/header/header';
import Signup from './pages/signup/signup';
import Login from './pages/login/login';

const App: React.FC = () => {
    return (
        <Router>
            <Header />
            <Routes>
                <Route path="/signup" element={<Signup />} />
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<h1 style={{ textAlign: 'center', marginTop: '20px' }}>Welcome to Crypto Arbitrage Bot</h1>} />
            </Routes>
        </Router>
    );
};

export default App;
