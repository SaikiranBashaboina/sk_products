import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, TextField, Button, CircularProgress,
  Grid, Avatar, IconButton,
} from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import DeleteIcon from '@mui/icons-material/Delete';
import { orderApi } from '../api/orderApi';
import { useSnackbar } from 'notistack';
import { profileApi } from '../api/profileApi';

export default function AddOrderPage() {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const fileInputRef = useRef(null);
  const [form, setForm] = useState({ title: '', description: '', quantity: 1, price: '', stock_status: 'IN_STOCK' });
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageName, setImageName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.title.trim()) errs.title = 'Title is required';
    if (!form.quantity || form.quantity < 1) errs.quantity = 'Quantity must be > 0';
    if (!form.price || parseFloat(form.price) <= 0) errs.price = 'Price must be > 0';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setImageName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      setImagePreview(event.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setImageFile(null);
    setImagePreview(null);
    setImageName('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      let imageFilename = null;

      // Upload image first if selected
      if (imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        const uploadRes = await profileApi.uploadImage(imageFile);
        imageFilename = uploadRes.data.profile_image;
      }

      await orderApi.createOrder({
        ...form,
        price: parseFloat(form.price),
        quantity: parseInt(form.quantity),
        image: imageFilename,
      });
      enqueueSnackbar('Order created successfully!', { variant: 'success' });
      navigate('/orders');
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to create order', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Card sx={{ borderRadius: 3, maxWidth: 600 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight={600} gutterBottom>Add New Order</Typography>
          <form onSubmit={handleSubmit}>
            <TextField fullWidth label="Title" value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              error={!!errors.title} helperText={errors.title} sx={{ mb: 2 }} required />
            <TextField fullWidth label="Description" value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              multiline rows={3} sx={{ mb: 2 }} />
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField fullWidth label="Quantity" type="number" value={form.quantity}
                  onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                  error={!!errors.quantity} helperText={errors.quantity} required />
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth label="Price" type="number" value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                  error={!!errors.price} helperText={errors.price} inputProps={{ step: '0.01' }} required />
              </Grid>
            </Grid>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>Stock Status</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant={form.stock_status === 'IN_STOCK' ? 'contained' : 'outlined'}
                  onClick={() => setForm({ ...form, stock_status: 'IN_STOCK' })}
                  color="success"
                  size="small"
                  sx={{ minWidth: 120 }}
                >
                  {form.stock_status === 'IN_STOCK' ? '✓ In Stock' : 'In Stock'}
                </Button>
                <Button
                  variant={form.stock_status === 'OUT_OF_STOCK' ? 'contained' : 'outlined'}
                  onClick={() => setForm({ ...form, stock_status: 'OUT_OF_STOCK' })}
                  color="error"
                  size="small"
                  sx={{ minWidth: 120 }}
                >
                  {form.stock_status === 'OUT_OF_STOCK' ? '✓ Out of Stock' : 'Out of Stock'}
                </Button>
              </Box>
            </Box>

            {/* Image Upload */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>Order Image (optional)</Typography>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                style={{ display: 'none' }}
                id="order-image-input"
              />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <label htmlFor="order-image-input">
                  <Button variant="outlined" component="span" startIcon={<PhotoCameraIcon />}>
                    Choose Image
                  </Button>
                </label>
                {imageName && (
                  <Typography variant="caption" color="text.secondary">{imageName}</Typography>
                )}
                {imagePreview && (
                  <IconButton onClick={handleRemoveImage} size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>
              {imagePreview && (
                <Box sx={{ mt: 2, position: 'relative', display: 'inline-block' }}>
                  <img src={imagePreview} alt="Preview"
                    style={{ maxHeight: 200, maxWidth: '100%', borderRadius: 8, objectFit: 'cover' }} />
                </Box>
              )}
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <Button type="submit" variant="contained" disabled={loading}>
                {loading ? <CircularProgress size={20} /> : 'Create Order'}
              </Button>
              <Button variant="outlined" onClick={() => navigate('/orders')}>Cancel</Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}