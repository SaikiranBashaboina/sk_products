import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import theme from './theme/theme';
import { ProtectedRoute, AdminRoute, IdentityOrAdminRoute } from './routes/ProtectedRoute';
import DashboardLayout from './layouts/DashboardLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import OrdersPage from './pages/OrdersPage';
import OrderDetailsPage from './pages/OrderDetailsPage';
import MyOrdersPage from './pages/MyOrdersPage';
import AddOrderPage from './pages/AddOrderPage';
import EditOrderPage from './pages/EditOrderPage';
import OrdersManagementPage from './pages/OrdersManagementPage';
import UsersPage from './pages/UsersPage';
import IdentityPage from './pages/IdentityPage';
import ProfilePage from './pages/ProfilePage';

function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: '4rem' }}>
      <h1>404</h1>
      <p>Page not found</p>
    </div>
  );
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        autoHideDuration={3000}>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <Router>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="orders" element={<OrdersPage />} />
                <Route path="orders/:id" element={<OrderDetailsPage />} />
                <Route path="my-orders" element={<MyOrdersPage />} />
                <Route path="add-order" element={
                  <AdminRoute><AddOrderPage /></AdminRoute>
                } />
                <Route path="edit-order/:id" element={
                  <AdminRoute><EditOrderPage /></AdminRoute>
                } />
                <Route path="orders-management" element={
                  <AdminRoute><OrdersManagementPage /></AdminRoute>
                } />
                <Route path="users" element={
                  <IdentityOrAdminRoute><UsersPage /></IdentityOrAdminRoute>
                } />
                <Route path="identity" element={
                  <IdentityOrAdminRoute><IdentityPage /></IdentityOrAdminRoute>
                } />
                <Route path="profile" element={<ProfilePage />} />
              </Route>
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Router>
        </AuthProvider>
      </QueryClientProvider>
      </SnackbarProvider>
    </ThemeProvider>
  );
}
