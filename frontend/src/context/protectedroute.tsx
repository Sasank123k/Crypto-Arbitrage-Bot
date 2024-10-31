import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './authcontext';

interface ProtectedRouteProps {
    children: JSX.Element;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        // Redirect to login if the user is not authenticated
        return <Navigate to="/login" />;
    }

    return children;
};

export default ProtectedRoute;
