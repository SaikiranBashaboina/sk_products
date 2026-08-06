import { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, CircularProgress,
  TablePagination, Select, MenuItem, FormControl, InputLabel, IconButton, Tooltip,
  Switch, FormControlLabel,
} from '@mui/material';
import { orderApi } from '../api/orderApi';
import { useSnackbar } from 'notistack';

const statusColors = {
  ORDERED: 'warning',
  PROCESSED: 'info',
  DELIVERED: 'success',
  CANCELLED: 'error',
};

export default function OrdersManagementPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await orderApi.getAllUserOrders(page + 1, pageSize, statusFilter);
      setOrders(res.data.user_orders);
      setTotal(res.data.total);
    } catch {
      enqueueSnackbar('Failed to load orders', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, [page, pageSize, statusFilter]);

  const handleStatusChange = async (userOrderId, newStatus) => {
    try {
      await orderApi.updateOrderStatus(userOrderId, newStatus);
      enqueueSnackbar('Status updated', { variant: 'success' });
      fetchOrders();
    } catch {
      enqueueSnackbar('Failed to update status', { variant: 'error' });
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Status</InputLabel>
          <Select value={statusFilter} label="Filter by Status" onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="ORDERED">ORDERED</MenuItem>
            <MenuItem value="PROCESSED">PROCESSED</MenuItem>
            <MenuItem value="DELIVERED">DELIVERED</MenuItem>
            <MenuItem value="CANCELLED">CANCELLED</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Order</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Quantity</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Price</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Stock</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow><TableCell colSpan={7} align="center" sx={{ py: 4 }}><CircularProgress /></TableCell></TableRow>
                ) : orders.length === 0 ? (
                  <TableRow><TableCell colSpan={7} align="center" sx={{ py: 4 }}>No orders found</TableCell></TableRow>
                ) : orders.map((uo) => (
                  <TableRow key={uo.id} hover>
                    <TableCell>{uo.user_name}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>{uo.order?.title}</Typography>
                    </TableCell>
                    <TableCell>{uo.order?.quantity}</TableCell>
                    <TableCell>₹{uo.order?.price?.toFixed(2)}</TableCell>
                    <TableCell>
                      <Chip label={uo.status} color={statusColors[uo.status] || 'default'} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={uo.order?.stock_status === 'IN_STOCK' ? 'In Stock' : 'Out of Stock'}
                        size="small"
                        color={uo.order?.stock_status === 'IN_STOCK' ? 'success' : 'error'}
                      />
                    </TableCell>
                    <TableCell><Typography variant="caption">{new Date(uo.created_at).toLocaleDateString()}</Typography></TableCell>
                    <TableCell>
                      {uo.status !== 'CANCELLED' && uo.status !== 'DELIVERED' && (
                        <FormControl size="small" sx={{ minWidth: 120 }}>
                          <Select
                            value={uo.status}
                            onChange={(e) => handleStatusChange(uo.id, e.target.value)}
                            size="small"
                          >
                            {uo.status === 'ORDERED' && <MenuItem value="PROCESSED">Process</MenuItem>}
                            {uo.status === 'PROCESSED' && <MenuItem value="DELIVERED">Deliver</MenuItem>}
                            {(uo.status === 'ORDERED' || uo.status === 'PROCESSED') && (
                              <MenuItem value="CANCELLED">Cancel</MenuItem>
                            )}
                          </Select>
                        </FormControl>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination component="div" count={total} page={page} onPageChange={(e, p) => setPage(p)}
            rowsPerPage={pageSize} onRowsPerPageChange={(e) => { setPageSize(parseInt(e.target.value)); setPage(0); }} />
        </CardContent>
      </Card>
    </Box>
  );
}