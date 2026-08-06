import api from './axios';

export const userApi = {
  getUsers: (page = 1, pageSize = 10, search = '') => {
    const params = { page, page_size: pageSize };
    if (search) params.search = search;
    return api.get('/users', { params });
  },
  getUser: (id) => api.get(`/users/${id}`),
  createUser: (data) => api.post('/users', data),
  updateUser: (id, data) => api.put(`/users/${id}`, data),
  deleteUser: (id) => api.delete(`/users/${id}`),
  updateRoles: (id, roles) => api.put(`/users/${id}/roles`, { roles }),
  resetPassword: (id, newPassword) => api.post(`/users/${id}/reset-password`, { new_password: newPassword }),
};