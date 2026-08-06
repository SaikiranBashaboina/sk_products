import { useState } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Button, CircularProgress,
  Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, Avatar, TablePagination, InputAdornment, IconButton,
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useAuth } from '../contexts/AuthContext';
import { userApi } from '../api/userApi';
import { useSnackbar } from 'notistack';
import { useEffect } from 'react';

export default function IdentityPage() {
  const { enqueueSnackbar } = useSnackbar();
  const { isAdmin, isIdentity } = useAuth();
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '', address: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [creating, setCreating] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await userApi.getUsers(page + 1, pageSize);
      setUsers(res.data.users);
      setTotal(res.data.total);
    } catch {
      enqueueSnackbar('Failed to load users', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, [page, pageSize]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.password) {
      enqueueSnackbar('Name, Email and Password are required', { variant: 'warning' });
      return;
    }
    setCreating(true);
    try {
      await userApi.createUser(form);
      enqueueSnackbar('User created successfully!', { variant: 'success' });
      setForm({ name: '', email: '', password: '', phone: '', address: '' });
      fetchUsers();
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to create user', { variant: 'error' });
    } finally {
      setCreating(false);
    }
  };

  return (
    <Box>
      <Card sx={{ borderRadius: 3, mb: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>Create New User</Typography>
          <form onSubmit={handleCreate}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField fullWidth size="small" label="Name" value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField fullWidth size="small" label="Email" type="email" value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField fullWidth size="small" label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Phone" value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Address" value={form.address}
                  onChange={(e) => setForm({ ...form, address: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <Button type="submit" variant="contained" startIcon={<PersonAddIcon />} disabled={creating}>
                  {creating ? <CircularProgress size={20} /> : 'Create User'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <Typography variant="h6" sx={{ p: 3, pb: 1 }}>Identity Users</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Email</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Roles</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Identity ID</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.filter(u => u.identity_uuid).map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 12 }}>
                          {user.name?.charAt(0)?.toUpperCase()}
                        </Avatar>
                        <Typography variant="body2">{user.name}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      {user.roles?.map(r => <Chip key={r} label={r} size="small" color={r === 'ADMIN' ? 'error' : 'info'} sx={{ mr: 0.5 }} />)}
                    </TableCell>
                    <TableCell>
                      <Chip label={user.identity_uuid} size="small" variant="outlined" color="info" />
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