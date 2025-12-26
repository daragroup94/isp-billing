export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface Customer {
  id: number;
  customer_code: string;
  full_name: string;
  email: string | null;
  phone: string;
  address: string;
  city: string;
  province: string;
  package_id: number | null;
  status: 'active' | 'suspended' | 'inactive' | 'terminated';
  is_active: boolean;
  created_at: string;
}

export interface Package {
  id: number;
  name: string;
  code: string;
  description: string | null;
  download_speed: number;
  upload_speed: number;
  price: number;
  installation_fee: number;
  quota_gb: number;
  is_active: boolean;
  package_type: 'residential' | 'business' | 'corporate';
}

export interface Invoice {
  id: number;
  invoice_number: string;
  customer_id: number;
  billing_period: string;
  invoice_date: string;
  due_date: string;
  total_amount: number;
  paid_amount: number;
  status: 'pending' | 'paid' | 'partial' | 'overdue' | 'cancelled';
  created_at: string;
}

export interface Payment {
  id: number;
  payment_number: string;
  customer_id: number;
  invoice_id: number | null;
  payment_date: string;
  amount: number;
  payment_method: string;
  status: 'pending' | 'verified' | 'rejected' | 'cancelled';
  created_at: string;
}

export interface DashboardStats {
  customers: {
    total: number;
    active: number;
    suspended: number;
    growth_rate: number;
  };
  invoices: {
    total: number;
    pending: number;
    paid: number;
    overdue: number;
