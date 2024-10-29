import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/header/header';
import Footer from './components/footer/footer';
import Home from './pages/home/home';
import Login from './pages/login/login';
import Signup from './pages/signup/signup';
import Dashboard from './pages/dashboard/dashboard';


const App: React.FC = () => {
    return (
        <Router>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
                <Header />
                <main style={{ flex: 1, paddingTop: '60px', display: 'flex', justifyContent: 'center' }}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                        <Route path="/dashboard" element={<Dashboard />} />

                    </Routes>
                </main>
                <Footer />
            </div>
        </Router>
    );
};

export default App;
