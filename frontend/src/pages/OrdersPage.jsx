import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, TextField, Button, Chip,
  CircularProgress, Grid, CardMedia, CardActions, IconButton, Tooltip,
  Avatar, Rating, FormControl, InputLabel, Select, MenuItem,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddShoppingCartIcon from '@mui/icons-material/AddShoppingCart';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import InventoryIcon from '@mui/icons-material/Inventory';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { orderApi } from '../api/orderApi';
import { useAuth } from '../contexts/AuthContext';
import { useSnackbar } from 'notistack';

export default function OrdersPage() {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const { isAdmin } = useAuth();
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize] = useState(12);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [stockFilter, setStockFilter] = useState('');

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await orderApi.getOrders(page + 1, pageSize, search);
      setOrders(res.data.orders);
      setTotal(res.data.total);
    } catch (err) {
      enqueueSnackbar('Failed to load orders', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, [page, search, stockFilter]);

  const handleSearch = () => {
    setSearch(searchInput);
    setPage(0);
  };

  const handleStockFilterChange = (e) => {
    setStockFilter(e.target.value);
    setPage(0);
  };

  const handleSelect = async (orderId) => {
    try {
      await orderApi.selectOrder(orderId);
      enqueueSnackbar('Order placed successfully!', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to place order', { variant: 'error' });
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <Box>
      {/* Search Bar */}
      <Card sx={{ borderRadius: 3, mb: 3, p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField size="small" placeholder="Search orders by title or description..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            sx={{ minWidth: { xs: '100%', sm: 350 } }} />
          <Button variant="contained" startIcon={<SearchIcon />} onClick={handleSearch}>
            Search
          </Button>
          {search && (
            <Button variant="text" onClick={() => { setSearch(''); setSearchInput(''); }}>
              Clear
            </Button>
          )}
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Stock Status</InputLabel>
            <Select value={stockFilter} label="Stock Status" onChange={handleStockFilterChange}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="IN_STOCK">In Stock</MenuItem>
              <MenuItem value="OUT_OF_STOCK">Out of Stock</MenuItem>
            </Select>
          </FormControl>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
            {total} order{total !== 1 ? 's' : ''} found
          </Typography>
        </Box>
      </Card>

      {/* Order Cards Grid */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      ) : orders.length === 0 ? (
        <Card sx={{ borderRadius: 3, p: 6, textAlign: 'center' }}>
          <InventoryIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">No orders available</Typography>
          <Typography variant="body2" color="text.disabled">
            {search ? 'Try a different search term.' : 'Check back later for new orders.'}
          </Typography>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {orders.map((order) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={order.id}>
              <Card sx={{
                borderRadius: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.12)',
                },
              }}>
                {/* Image */}
                <Box sx={{
                  height: 180,
                  bgcolor: order.image ? 'transparent' : 'grey.100',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                }}>
                  {order.image ? (
                    <CardMedia
                      component="img"
                      height="180"
                      image={`/uploads/${order.image}`}
                      alt={order.title}
                      sx={{ objectFit: 'cover' }}
                    />
                  ) : (
                    <InventoryIcon sx={{ fontSize: 48, color: 'text.disabled' }} />
                  )}
                </Box>

                <CardContent sx={{ flexGrow: 1, pb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="h6" fontWeight={600} gutterBottom noWrap sx={{ flex: 1 }}>
                      {order.title}
                    </Typography>
                    <Chip
                      icon={order.stock_status === 'IN_STOCK' ? <CheckCircleIcon /> : <BlockIcon />}
                      label={order.stock_status === 'IN_STOCK' ? 'In Stock' : 'Out of Stock'}
                      size="small"
                      color={order.stock_status === 'IN_STOCK' ? 'success' : 'error'}
                      sx={{ ml: 1, flexShrink: 0 }}
                    />
                  </Box>
                  {order.description && (
                    <Typography variant="body2" color="text.secondary" sx={{
                      mb: 1.5,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}>
                      {order.description}
                    </Typography>
                  )}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                    <Box>
                      <Typography variant="h5" color="primary.main" fontWeight={700}>
                        ₹{order.price.toFixed(2)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Qty: {order.quantity}
                      </Typography>
                    </Box>
                    <Chip
                      label={new Date(order.created_at).toLocaleDateString()}
                      size="small"
                      variant="outlined"
                      color="default"
                    />
                  </Box>
                </CardContent>

                <CardActions sx={{ px: 2, pb: 2, pt: 0, justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <Tooltip title="View Details">
                      <IconButton
                        onClick={() => navigate(`/orders/${order.id}`)}
                        size="small"
                        color="default"
                        sx={{ bgcolor: 'grey.100', '&:hover': { bgcolor: 'grey.200' } }}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {isAdmin() && (
                      <Tooltip title="Edit Order">
                        <IconButton
                          onClick={() => navigate(`/edit-order/${order.id}`)}
                          size="small"
                          color="info"
                          sx={{ bgcolor: 'info.50', '&:hover': { bgcolor: 'info.100' } }}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<AddShoppingCartIcon />}
                    onClick={() => handleSelect(order.id)}
                    disabled={order.stock_status === 'OUT_OF_STOCK'}
                    sx={{ borderRadius: 2, textTransform: 'none' }}
                  >
                    {order.stock_status === 'OUT_OF_STOCK' ? 'Out of Stock' : 'Order Now'}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 4, mb: 2 }}>
          <Button
            variant="outlined"
            disabled={page === 0}
            onClick={() => setPage(page - 1)}
            size="small"
          >
            Previous
          </Button>
          <Box sx={{ display: 'flex', alignItems: 'center', px: 2 }}>
            <Typography variant="body2">
              Page {page + 1} of {totalPages}
            </Typography>
          </Box>
          <Button
            variant="outlined"
            disabled={page >= totalPages - 1}
            onClick={() => setPage(page + 1)}
            size="small"
          >
            Next
          </Button>
        </Box>
      )}
    </Box>
  );
}