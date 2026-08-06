import { useState } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Button, CircularProgress,
  Grid, Avatar, Divider, InputAdornment, IconButton,
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useAuth } from '../contexts/AuthContext';
import { profileApi } from '../api/profileApi';
import { useSnackbar } from 'notistack';

export default function ProfilePage() {
  const { user, setUser } = useAuth();
  const { enqueueSnackbar } = useSnackbar();
  const [form, setForm] = useState({ name: user?.name || '', email: user?.email || '', phone: user?.phone || '', address: user?.address || '' });
  const [passwordForm, setPasswordForm] = useState({ currentPassword: '', newPassword: '' });
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [imageUploading, setImageUploading] = useState(false);

  const handleUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await profileApi.updateProfile(form);
      setUser(res.data);
      enqueueSnackbar('Profile updated!', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to update', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (!passwordForm.currentPassword || !passwordForm.newPassword) {
      enqueueSnackbar('Fill in both fields', { variant: 'warning' });
      return;
    }
    if (passwordForm.newPassword.length < 6) {
      enqueueSnackbar('Password must be at least 6 characters', { variant: 'warning' });
      return;
    }
    setPasswordLoading(true);
    try {
      await profileApi.changePassword(passwordForm.currentPassword, passwordForm.newPassword);
      enqueueSnackbar('Password changed!', { variant: 'success' });
      setPasswordForm({ currentPassword: '', newPassword: '' });
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to change password', { variant: 'error' });
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageUploading(true);
    try {
      const res = await profileApi.uploadImage(file);
      setUser({ ...user, profile_image: res.data.profile_image });
      enqueueSnackbar('Image uploaded!', { variant: 'success' });
    } catch {
      enqueueSnackbar('Failed to upload image', { variant: 'error' });
    } finally {
      setImageUploading(false);
    }
  };

  const imageUrl = user?.profile_image ? `/uploads/${user.profile_image}` : undefined;

  return (
    <Box>
      <Card sx={{ borderRadius: 3, maxWidth: 700, mb: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 3 }}>
            <Box sx={{ position: 'relative' }}>
              <Avatar src={imageUrl} sx={{ width: 80, height: 80, bgcolor: 'primary.main', fontSize: 32 }}>
                {user?.name?.charAt(0)?.toUpperCase()}
              </Avatar>
              {imageUploading && <CircularProgress size={80} sx={{ position: 'absolute', top: 0, left: 0 }} />}
            </Box>
            <Box>
              <Typography variant="h6" fontWeight={600}>{user?.name}</Typography>
              <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
              <Button variant="outlined" size="small" component="label" sx={{ mt: 1 }}>
                Upload Photo
                <input type="file" hidden accept="image/*" onChange={handleImageUpload} />
              </Button>
            </Box>
          </Box>

          <Divider sx={{ mb: 3 }} />

          <form onSubmit={handleUpdate}>
            <Typography variant="h6" gutterBottom>Edit Profile</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Name" value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Email" type="email" value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })} />
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
                <Button type="submit" variant="contained" disabled={loading}>
                  {loading ? <CircularProgress size={20} /> : 'Save Changes'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 3, maxWidth: 700 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom>Change Password</Typography>
          <form onSubmit={handlePasswordChange}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Current Password"
                  type={showCurrentPassword ? 'text' : 'password'}
                  value={passwordForm.currentPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowCurrentPassword(!showCurrentPassword)} edge="end" size="small">
                          {showCurrentPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="New Password"
                  type={showNewPassword ? 'text' : 'password'}
                  value={passwordForm.newPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowNewPassword(!showNewPassword)} edge="end" size="small">
                          {showNewPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }} />
              </Grid>
              <Grid item xs={12}>
                <Button type="submit" variant="contained" disabled={passwordLoading}>
                  {passwordLoading ? <CircularProgress size={20} /> : 'Change Password'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}