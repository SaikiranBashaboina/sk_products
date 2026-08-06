import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, TextField, Button, CircularProgress,
  Grid, IconButton,
} from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import DeleteIcon from '@mui/icons-material/Delete';
import { orderApi } from '../api/orderApi';
import { profileApi } from '../api/profileApi';
import { useSnackbar } from 'notistack';

export default function EditOrderPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const fileInputRef = useRef(null);
  const [form, setForm] = useState({ title: '', description: '', quantity: 1, price: '', stock_status: 'IN_STOCK' });
  const [existingImage, setExistingImage] = useState(null);
  const [newImageFile, setNewImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageName, setImageName] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const res = await orderApi.getOrder(id);
        const order = res.data;
        setForm({
          title: order.title,
          description: order.description || '',
          quantity: order.quantity,
          price: order.price.toString(),
          stock_status: order.stock_status || 'IN_STOCK',
        });
        if (order.image) {
          setExistingImage(order.image);
        }
      } catch {
        enqueueSnackbar('Order not found', { variant: 'error' });
        navigate('/orders');
      } finally {
        setLoading(false);
      }
    };
    fetchOrder();
  }, [id]);

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
    setNewImageFile(file);
    setImageName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      setImagePreview(event.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setNewImageFile(null);
    setImagePreview(null);
    setImageName('');
    setExistingImage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSaving(true);
    try {
      let imageFilename = existingImage;

      // Upload new image if selected
      if (newImageFile) {
        const uploadRes = await profileApi.uploadImage(newImageFile);
        imageFilename = uploadRes.data.profile_image;
      }

      await orderApi.updateOrder(id, {
        title: form.title,
        description: form.description || null,
        quantity: parseInt(form.quantity),
        price: parseFloat(form.price),
        image: imageFilename,
      });
      enqueueSnackbar('Order updated successfully!', { variant: 'success' });
      navigate('/orders');
    } catch (err) {
      enqueueSnackbar(err.response?.data?.detail || 'Failed to update order', { variant: 'error' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  }

  const currentPreview = imagePreview || (existingImage ? `/uploads/${existingImage}` : null);

  return (
    <Box>
      <Card sx={{ borderRadius: 3, maxWidth: 600 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight={600} gutterBottom>Edit Order</Typography>
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
                    {existingImage || newImageFile ? 'Change Image' : 'Choose Image'}
                  </Button>
                </label>
                {imageName && (
                  <Typography variant="caption" color="text.secondary">{imageName}</Typography>
                )}
                {currentPreview && (
                  <IconButton onClick={handleRemoveImage} size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>
              {currentPreview && (
                <Box sx={{ mt: 2, position: 'relative', display: 'inline-block' }}>
                  <img src={currentPreview} alt="Preview"
                    style={{ maxHeight: 200, maxWidth: '100%', borderRadius: 8, objectFit: 'cover' }} />
                </Box>
              )}
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <Button type="submit" variant="contained" disabled={saving}>
                {saving ? <CircularProgress size={20} /> : 'Save Changes'}
              </Button>
              <Button variant="outlined" onClick={() => navigate('/orders')}>Cancel</Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}