import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Button, Chip, CircularProgress, Grid,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { orderApi } from '../api/orderApi';
import { useSnackbar } from 'notistack';

export default function OrderDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const res = await orderApi.getOrder(id);
        setOrder(res.data);
      } catch {
        enqueueSnackbar('Order not found', { variant: 'error' });
      } finally {
        setLoading(false);
      }
    };
    fetchOrder();
  }, [id]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if (!order) return <Typography>Order not found</Typography>;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/orders')} sx={{ mb: 2 }}>Back</Button>
      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight={600} gutterBottom>{order.title}</Typography>
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">Order ID</Typography>
              <Typography variant="body2">{order.uuid}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">Quantity</Typography>
              <Typography variant="body2">{order.quantity}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">Price</Typography>
              <Typography variant="body2" fontWeight={600}>₹{order.price.toFixed(2)}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="text.secondary">Created</Typography>
              <Typography variant="body2">{new Date(order.created_at).toLocaleString()}</Typography>
            </Grid>
            {order.description && (
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary">Description</Typography>
                <Typography variant="body2">{order.description}</Typography>
              </Grid>
            )}
            {order.image && (
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary">Image</Typography>
                <Box sx={{ mt: 1 }}>
                  <img src={`/uploads/${order.image}`} alt={order.title} style={{ maxWidth: 300, borderRadius: 8 }} />
                </Box>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}