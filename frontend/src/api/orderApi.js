import api from './axios';

export const orderApi = {
  getOrders: (page = 1, pageSize = 10, search = '') => {
    const params = { page, page_size: pageSize };
    if (search) params.search = search;
    return api.get('/orders', { params });
  },
  getOrder: (id) => api.get(`/orders/${id}`),
  createOrder: (data) => api.post('/orders', data),
  updateOrder: (id, data) => api.put(`/orders/${id}`, data),
  deleteOrder: (id) => api.delete(`/orders/${id}`),
  selectOrder: (orderId) => api.post(`/orders/${orderId}/select`),
  getMyOrders: (page = 1, pageSize = 10) => api.get('/orders/my/list', { params: { page, page_size: pageSize } }),
  cancelMyOrder: (userOrderId) => api.patch(`/orders/my/${userOrderId}/cancel`),
  getAllUserOrders: (page = 1, pageSize = 10, status = '') => {
    const params = { page, page_size: pageSize };
    if (status) params.status = status;
    return api.get('/orders/admin/all', { params });
  },
  updateOrderStatus: (userOrderId, status) => api.patch(`/orders/admin/${userOrderId}/status`, { status }),
  updateStockStatus: (orderId, stockStatus) => api.patch(`/orders/${orderId}/stock`, { stock_status: stockStatus }),
};
