import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: { username: string; password: string }) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  },
};

// Dashboard API
export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
  
  getRevenueChart: async (months: number = 12) => {
    const response = await api.get('/dashboard/revenue-chart', { params: { months } });
    return response.data;
  },
  
  getCustomerGrowth: async (months: number = 12) => {
    const response = await api.get('/dashboard/customer-growth', { params: { months } });
    return response.data;
  },
  
  getPackageDistribution: async () => {
    const response = await api.get('/dashboard/package-distribution');
    return response.data;
  },
  
  getRecentActivities: async (limit: number = 10) => {
    const response = await api.get('/dashboard/recent-activities', { params: { limit } });
    return response.data;
  },
};

// Customer API
export const customerApi = {
  getAll: async (filters?: any) => {
    const response = await api.get('/customers', { params: filters });
    return response.data;
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/customers/${id}`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/customers', data);
    return response.data;
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/customers/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number) => {
    await api.delete(`/customers/${id}`);
  },
  
  suspend: async (id: number) => {
    const response = await api.post(`/customers/${id}/suspend`);
    return response.data;
  },
  
  activate: async (id: number) => {
    const response = await api.post(`/customers/${id}/activate`);
    return response.data;
  },
  
  getCount: async () => {
    const response = await api.get('/customers/count');
    return response.data;
  },
};

// Package API
export const packagesAPI = {
  getList: async (params?: any) => {
    const response = await api.get('/packages', { params });
    return response.data;
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/packages/${id}`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/packages', data);
    return response.data;
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/packages/${id}`, data);
    return response.data;
  },
  
  delete: async (id: number) => {
    await api.delete(`/packages/${id}`);
  },
  
  toggle: async (id: number) => {
    const response = await api.post(`/packages/${id}/toggle`);
    return response.data;
  },
  
  getCount: async () => {
    const response = await api.get('/packages/count');
    return response.data;
  },
};

// Invoice API
export const invoicesAPI = {
  getList: async (params?: any) => {
    const response = await api.get('/invoices', { params });
    return response.data;
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/invoices/${id}`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/invoices', data);
    return response.data;
  },
  
  generate: async (data: { customer_id: number; billing_month: string }) => {
    const response = await api.post('/invoices/generate', data);
    return response.data;
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/invoices/${id}`, data);
    return response.data;
  },
  
  cancel: async (id: number) => {
    const response = await api.post(`/invoices/${id}/cancel`);
    return response.data;
  },
  
  markPaid: async (id: number) => {
    const response = await api.post(`/invoices/${id}/mark-paid`);
    return response.data;
  },
  
  getCount: async () => {
    const response = await api.get('/invoices/count');
    return response.data;
  },
};

// Payment API
export const paymentsAPI = {
  getList: async (params?: any) => {
    const response = await api.get('/payments', { params });
    return response.data;
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/payments/${id}`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/payments', data);
    return response.data;
  },
  
  verify: async (id: number, admin_notes?: string) => {
    const response = await api.post(`/payments/${id}/verify`, { admin_notes });
    return response.data;
  },
  
  reject: async (id: number, rejection_reason: string, admin_notes?: string) => {
    const response = await api.post(`/payments/${id}/reject`, { rejection_reason, admin_notes });
    return response.data;
  },
  
  cancel: async (id: number) => {
    const response = await api.post(`/payments/${id}/cancel`);
    return response.data;
  },
  
  getCount: async () => {
    const response = await api.get('/payments/count');
    return response.data;
  },
};

export default api;
