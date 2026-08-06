import { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TextField, Button, Chip, Avatar,
  CircularProgress, TablePagination, IconButton, Tooltip, Dialog,
  DialogTitle, DialogContent, DialogActions, Grid, Switch, FormControlLabel,
  InputAdornment,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import DeleteIcon from '@mui/icons-material/Delete';
import LockResetIcon from '@mui/icons-material/LockReset';
import EditIcon from '@mui/icons-material/Edit';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { userApi } from '../api/userApi';
import { useAuth } from '../contexts/AuthContext';
import { profileApi } from '../api/profileApi';
import { useSnackbar } from 'notistack';

export default function UsersPage() {
  const { enqueueSnackbar } = useSnackbar();
  const { isAdmin, isIdentity } = useAuth();
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [roleDialog, setRoleDialog] = useState(null);
  const [passwordDialog, setPasswordDialog] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [editDialog, setEditDialog] = useState(null);
  const [editForm, setEditForm] = useState({ name: '', email: '', phone: '', address: '' });
  const [saving, setSaving] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await userApi.getUsers(page + 1, pageSize, search);
      setUsers(res.data.users);
      setTotal(res.data.total);
    } catch {
      enqueueSnackbar('Failed to load users', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, [page, pageSize]);

  const handleSearch = () => { setPage(0); fetchUsers(); };

  const handleRoleToggle = async (role) => {
    const currentRoles = [...roleDialog.roles];
    const idx = currentRoles.indexOf(role);
    if (idx >= 0) currentRoles.splice(idx, 1);
    else currentRoles.push(role);
    try {
      const res = await userApi.updateRoles(roleDialog.id, currentRoles);
      enqueueSnackbar('Roles updated', { variant: 'success' });
      setRoleDialog({ ...roleDialog, roles: res.data.roles });
      fetchUsers();
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to update roles', { variant: 'error' });
    }
  };

  const handleResetPassword = async () => {
    if (!newPassword || newPassword.length < 6) {
      enqueueSnackbar('Password must be at least 6 characters', { variant: 'warning' });
      return;
    }
    try {
      await userApi.resetPassword(passwordDialog.id, newPassword);
      enqueueSnackbar('Password reset successfully', { variant: 'success' });
      setPasswordDialog(null);
      setNewPassword('');
    } catch {
      enqueueSnackbar('Failed to reset password', { variant: 'error' });
    }
  };

  const openEditDialog = (user) => {
    setEditDialog(user);
    setEditForm({ name: user.name, email: user.email, phone: user.phone || '', address: user.address || '' });
  };

  const handleEditSave = async () => {
    if (!editForm.name.trim()) {
      enqueueSnackbar('Name is required', { variant: 'warning' });
      return;
    }
    setSaving(true);
    try {
      await userApi.updateUser(editDialog.id, editForm);
      enqueueSnackbar('User updated successfully', { variant: 'success' });
      setEditDialog(null);
      fetchUsers();
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to update user', { variant: 'error' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
        <TextField size="small" placeholder="Search users..." value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          sx={{ minWidth: 300 }} />
        <Button variant="contained" startIcon={<SearchIcon />} onClick={handleSearch}>Search</Button>
      </Box>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Email</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Roles</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow><TableCell colSpan={5} align="center" sx={{ py: 4 }}><CircularProgress /></TableCell></TableRow>
                ) : users.length === 0 ? (
                  <TableRow><TableCell colSpan={5} align="center" sx={{ py: 4 }}>No users found</TableCell></TableRow>
                ) : users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar src={user.profile_image ? `/uploads/${user.profile_image}` : undefined}
                          sx={{ width: 36, height: 36, bgcolor: 'primary.main', fontSize: 14 }}>
                          {user.name?.charAt(0)?.toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight={500}>{user.name}</Typography>
                          {user.identity_uuid && <Typography variant="caption" color="text.secondary">{user.identity_uuid}</Typography>}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell><Typography variant="body2">{user.email}</Typography></TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {user.roles?.map(role => (
                          <Chip key={role} label={role} size="small"
                            color={role === 'ADMIN' ? 'error' : role === 'IDENTITY' ? 'info' : 'default'} />
                        ))}
                        {(!user.roles || user.roles.length === 0) && <Chip label="Normal User" size="small" variant="outlined" />}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={user.active ? 'Active' : 'Inactive'} size="small"
                        color={user.active ? 'success' : 'default'} />
                    </TableCell>
                    <TableCell>
                      {(isAdmin() || isIdentity()) && (
                        <>
                          <Tooltip title="Manage Roles">
                            <IconButton onClick={() => setRoleDialog(user)} size="small" color="primary">
                              <AdminPanelSettingsIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit User">
                            <IconButton onClick={() => openEditDialog(user)} size="small" color="info">
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reset Password">
                            <IconButton onClick={() => setPasswordDialog(user)} size="small" color="warning">
                              <LockResetIcon />
                            </IconButton>
                          </Tooltip>
                        </>
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

      {/* Role Dialog */}
      <Dialog open={!!roleDialog} onClose={() => setRoleDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Manage Roles - {roleDialog?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            {isAdmin() && (
              <FormControlLabel control={<Switch checked={roleDialog?.roles?.includes('ADMIN') || false}
                onChange={() => handleRoleToggle('ADMIN')} />} label="ADMIN" />
            )}
            <FormControlLabel control={<Switch checked={roleDialog?.roles?.includes('IDENTITY') || false}
              onChange={() => handleRoleToggle('IDENTITY')} />} label="IDENTITY" />
          </Box>
          {!isAdmin() && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
              You can only assign IDENTITY role.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoleDialog(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={!!editDialog} onClose={() => setEditDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit User - {editDialog?.name}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField fullWidth label="Name" value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} required />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Email" type="email" value={editForm.email}
                onChange={(e) => setEditForm({ ...editForm, email: e.target.value })} required />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Phone" value={editForm.phone}
                onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Address" value={editForm.address}
                onChange={(e) => setEditForm({ ...editForm, address: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(null)}>Cancel</Button>
          <Button onClick={handleEditSave} variant="contained" disabled={saving}>
            {saving ? <CircularProgress size={20} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Password Dialog */}
      <Dialog open={!!passwordDialog} onClose={() => setPasswordDialog(null)}>
        <DialogTitle>Reset Password - {passwordDialog?.name}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="New Password"
            type={showPassword ? 'text' : 'password'}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            sx={{ mt: 2 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialog(null)}>Cancel</Button>
          <Button onClick={handleResetPassword} variant="contained">Reset</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}