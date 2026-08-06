import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/axios';
import { useAuth } from '../contexts/AuthContext';

export function useOrders(page = 1, pageSize = 10, search = '') {
  return useQuery({
    queryKey: ['orders', page, pageSize, search],
    queryFn: async () => {
      const res = await api.get('/orders', { params: { page, page_size: pageSize, search } });
      return res.data;
    },
    keepPreviousData: true,
  });
}

export function useMyOrders(page = 1, pageSize = 10) {
  return useQuery({
    queryKey: ['myOrders', page, pageSize],
    queryFn: async () => {
      const res = await api.get('/my-orders', { params: { page, page_size: pageSize } });
      return res.data;
    },
    keepPreviousData: true,
  });
}

export function useUsers(page = 1, pageSize = 10, search = '') {
  return useQuery({
    queryKey: ['users', page, pageSize, search],
    queryFn: async () => {
      const res = await api.get('/users', { params: { page, page_size: pageSize, search } });
      return res.data;
    },
    enabled: useAuth().isAdmin() || useAuth().isIdentity(),
    keepPreviousData: true,
  });
}

export function useProfile() {
  const { user, refreshUser } = useAuth();
  return useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const res = await api.get('/profile');
      return res.data;
    },
    initialData: user,
    onSuccess: refreshUser,
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/orders', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      queryClient.invalidateQueries(['myOrders']);
    },
  });
}

export function useUpdateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(`/orders/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
    },
  });
}

export function useDeleteOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(`/orders/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
    },
  });
}

export function useSelectOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orderId) => api.post(`/orders/${orderId}/select`),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      queryClient.invalidateQueries(['myOrders']);
    },
  });
}

export function useCancelOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orderId) => api.patch(`/my-orders/${orderId}/cancel`),
    onSuccess: () => {
      queryClient.invalidateQueries(['myOrders']);
    },
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const { refreshUser } = useAuth();
  return useMutation({
    mutationFn: (data) => api.put('/profile', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['profile']);
      refreshUser();
    },
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (data) => api.put('/profile/password', data),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/users', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(`/users/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(`/users/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });
}

export function useUpdateUserRoles() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, roles }) => api.put(`/users/${id}/roles`, { roles }),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: ({ userId, newPassword }) => api.put(`/users/${userId}/reset-password`, { new_password: newPassword }),
  });
}