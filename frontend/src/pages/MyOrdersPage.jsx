import { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, CircularProgress,
  TablePagination, Button, IconButton, Tooltip, Dialog, DialogTitle,
  DialogContent, DialogActions,
} from '@mui/material';
import CancelIcon from '@mui/icons-material/Cancel';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { orderApi } from '../api/orderApi';
import { useSnackbar } from 'notistack';

const statusColors = {
  ORDERED: 'warning',
  PROCESSED: 'info',
  DELIVERED: 'success',
  CANCELLED: 'error',
};

export default function MyOrdersPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [loading, setLoading] = useState(true);
  const [cancelDialog, setCancelDialog] = useState(null);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await orderApi.getMyOrders(page + 1, pageSize);
      setOrders(res.data.user_orders);
      setTotal(res.data.total);
    } catch {
      enqueueSnackbar('Failed to load orders', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, [page, pageSize]);

  const handleCancel = async () => {
    if (!cancelDialog) return;
    try {
      await orderApi.cancelMyOrder(cancelDialog.id);
      enqueueSnackbar('Order cancelled', { variant: 'success' });
      setCancelDialog(null);
      fetchOrders();
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Cannot cancel', { variant: 'error' });
    }
  };

  return (
    <Box>
      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Order</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Quantity</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Price</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow><TableCell colSpan={6} align="center" sx={{ py: 4 }}><CircularProgress /></TableCell></TableRow>
                ) : orders.length === 0 ? (
                  <TableRow><TableCell colSpan={6} align="center" sx={{ py: 4 }}>No orders selected yet</TableCell></TableRow>
                ) : orders.map((uo) => (
                  <TableRow key={uo.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>{uo.order?.title}</Typography>
                    </TableCell>
                    <TableCell>{uo.order?.quantity}</TableCell>
                    <TableCell>₹{uo.order?.price?.toFixed(2)}</TableCell>
                    <TableCell>
                      <Chip label={uo.status} color={statusColors[uo.status] || 'default'} size="small" />
                    </TableCell>
                    <TableCell><Typography variant="caption">{new Date(uo.created_at).toLocaleDateString()}</Typography></TableCell>
                    <TableCell>
                      {uo.status === 'ORDERED' && (
                        <Tooltip title="Cancel Order">
                          <IconButton onClick={() => setCancelDialog(uo)} size="small" color="error">
                            <CancelIcon />
                          </IconButton>
                        </Tooltip>
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

      <Dialog open={!!cancelDialog} onClose={() => setCancelDialog(null)}>
        <DialogTitle>Cancel Order</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to cancel "{cancelDialog?.order?.title}"?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialog(null)}>No</Button>
          <Button onClick={handleCancel} color="error" variant="contained">Yes, Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}