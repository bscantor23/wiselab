import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import AuthLayout from './features/auth/components/AuthLayout';
import './styles/index.css';

import WorkspaceList from './features/workspaces/components/WorkspaceList';
import ProtectedRoute from './components/auth/ProtectedRoute';
import WorkInProgress from './components/ui/WorkInProgress';

function App() {
    return (
        <Provider store={store}>
            <BrowserRouter>
                <Routes>
                    {/* Auth Routes */}
                    <Route path="/auth" element={<AuthLayout />} />

                    {/* Protected Routes */}
                    <Route
                        path="/workspaces"
                        element={
                            <ProtectedRoute>
                                <WorkspaceList />
                            </ProtectedRoute>
                        }
                    />

                    {/* Work in Progress Placeholders */}
                    <Route
                        path="/work-in-progress"
                        element={
                            <ProtectedRoute>
                                <WorkInProgress />
                            </ProtectedRoute>
                        }
                    />

                    {/* Redirects */}
                    <Route path="/" element={<Navigate to="/workspaces" replace />} />
                    <Route path="/dashboard" element={<Navigate to="/workspaces" replace />} />

                    {/* Catch-all */}
                    <Route path="*" element={<Navigate to="/workspaces" replace />} />
                </Routes>
            </BrowserRouter>
        </Provider>
    );
}

export default App;
