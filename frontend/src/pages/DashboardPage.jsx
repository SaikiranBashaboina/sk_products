import { Box, Grid, Card, CardContent, Typography, CircularProgress, Skeleton } from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import ListAltIcon from '@mui/icons-material/ListAlt';
import PeopleIcon from '@mui/icons-material/People';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import { useAuth } from '../contexts/AuthContext';
import { useOrders, useMyOrders, useUsers } from '../hooks/useApi';

export default function DashboardPage() {
  const { user, isAdmin, isIdentity } = useAuth();

  const { data: ordersData, isLoading: ordersLoading } = useOrders(1, 1);
  const { data: myOrdersData, isLoading: myOrdersLoading } = useMyOrders(1, 1000);
  const { data: usersData, isLoading: usersLoading } = useUsers(1, 1);

  const loading = ordersLoading || myOrdersLoading || (isAdmin() && usersLoading);

  const stats = {
    orders: ordersData?.total || 0,
    myOrders: myOrdersData?.total || 0,
    users: usersData?.total || 0,
    processed: myOrdersData?.user_orders?.filter(o => o.status === 'PROCESSED' || o.status === 'DELIVERED').length || 0,
  };

  const cards = [
    { title: 'Total Orders', value: stats.orders, icon: <ShoppingCartIcon />, color: '#1976d2' },
    { title: 'My Orders', value: stats.myOrders, icon: <ListAltIcon />, color: '#388e3c' },
    { title: 'Processed/Delivered', value: stats.processed, icon: <LocalShippingIcon />, color: '#f57c00' },
    { title: 'Users', value: stats.users, icon: <PeopleIcon />, color: '#7b1fa2', show: isAdmin() || isIdentity() },
  ].filter(c => c.show !== false);

  if (loading) {
    return (
      <Box>
        <Skeleton variant="text" width={300} height={40} sx={{ mb: 3 }} />
        <Skeleton variant="text" width={400} height={20} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Card sx={{ borderRadius: 3 }}>
                <CardContent>
                  <Skeleton variant="text" width="60%" />
                  <Skeleton variant="text" width="40%" />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Welcome back, {user?.name}!
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Here's your order management overview.
      </Typography>

      <Grid container spacing={3}>
        {cards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={card.title}>
            <Card sx={{ borderRadius: 3 }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{
                  width: 56, height: 56, borderRadius: 2, display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  bgcolor: `${card.color}15`, color: card.color,
                }}>
                  {card.icon}
                </Box>
                <Box>
                  <Typography variant="h4" fontWeight={700}>{card.value}</Typography>
                  <Typography variant="body2" color="text.secondary">{card.title}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Quick Info</Typography>
            <Typography variant="body2" color="text.secondary">
              Role: {user?.roles?.length ? user.roles.join(', ') : 'Normal User'}
              {user?.identity_uuid ? ` | Identity: ${user.identity_uuid}` : ''}
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}