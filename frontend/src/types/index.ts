// User & Auth Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Customer Types
export interface Customer {
  id: number;
  customer_number: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  status: 'active' | 'suspended' | 'inactive';
  package_id?: number;
  package?: Package;
  installation_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerFilters {
  status?: string;
  package_id?: number;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface CustomerStats {
  total: number;
  active: number;
  suspended: number;
  inactive: number;
}

// Package Types
export interface Package {
  id: number;
  name: string;
  description?: string;
  speed_mbps: number;
  price: number;
  package_type: 'residential' | 'business' | 'corporate';
  is_active: boolean;
  features?: string[];
  created_at: string;
  updated_at: string;
}

export interface PackageFilters {
  is_active?: boolean;
  package_type?: string;
  skip?: number;
  limit?: number;
}

export interface PackageStats {
  total: number;
  active: number;
  inactive: number;
  residential: number;
  business: number;
  corporate: number;
}

// Invoice Types
export interface Invoice {
  id: number;
  invoice_number: string;
  customer_id: number;
  customer?: Customer;
  billing_month: string;
  package_price: number;
  additional_charges: number;
  discount: number;
  total_amount: number;
  paid_amount: number;
  outstanding_amount: number;
  status: 'pending' | 'paid' | 'partial' | 'overdue' | 'cancelled';
  due_date: string;
  paid_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface InvoiceFilters {
  customer_id?: number;
  status?: string;
  month?: string;
  skip?: number;
  limit?: number;
}

export interface InvoiceStats {
  total: number;
  pending: number;
  paid: number;
  partial: number;
  overdue: number;
  cancelled: number;
  total_outstanding: number;
  total_paid: number;
}

// Payment Types
export interface Payment {
  id: number;
  payment_number: string;
  invoice_id: number;
  invoice?: Invoice;
  customer_id: number;
  customer?: Customer;
  amount: number;
  payment_method: 'transfer' | 'cash' | 'card' | 'other';
  payment_date: string;
  status: 'pending' | 'verified' | 'rejected' | 'cancelled';
  proof_of_payment?: string;
  verified_by?: number;
  verified_at?: string;
  rejection_reason?: string;
  admin_notes?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentFilters {
  customer_id?: number;
  invoice_id?: number;
  status?: string;
  payment_method?: string;
  skip?: number;
  limit?: number;
}

export interface PaymentStats {
  total: number;
  pending: number;
  verified: number;
  rejected: number;
  cancelled: number;
  total_verified_amount: number;
  pending_amount: number;
}

// Dashboard Types
export interface DashboardStats {
  customers: CustomerStats;
  invoices: InvoiceStats;
  payments: PaymentStats;
  revenue: {
    current_month: number;
    previous_month: number;
    growth_percentage: number;
  };
}

// Common Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface FormErrors {
  [key: string]: string;
}

// Utility Types
export type Status = 'active' | 'inactive' | 'suspended' | 'pending';
export type PaymentStatus = 'pending' | 'verified' | 'rejected' | 'cancelled';
export type InvoiceStatus = 'pending' | 'paid' | 'partial' | 'overdue' | 'cancelled';
export type PackageType = 'residential' | 'business' | 'corporate';
export type PaymentMethod = 'transfer' | 'cash' | 'card' | 'other';
