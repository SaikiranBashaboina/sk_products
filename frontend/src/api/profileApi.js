import api from './axios';

export const profileApi = {
  getProfile: () => api.get('/profile'),
  updateProfile: (data) => api.put('/profile', data),
  changePassword: (currentPassword, newPassword) =>
    api.post('/profile/change-password', { current_password: currentPassword, new_password: newPassword }),
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/profile/upload-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};