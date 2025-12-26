'use client';

import { useDashboard } from '@/hooks/useDashboard';
import { formatCurrency } from '@/lib/utils';

export default function DashboardPage() {
  const { stats, loading, error } = useDashboard();

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-gray-500 text-sm font-medium">Total Customers</h3>
          <p className="text-2xl font-bold mt-2">{stats.customers.total}</p>
          <p className="text-sm text-gray-500 mt-1">{stats.customers.active} active</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-gray-500 text-sm font-medium">Total Revenue</h3>
          <p className="text-2xl font-bold mt-2">{formatCurrency(stats.revenue.total)}</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-gray-500 text-sm font-medium">Pending Invoices</h3>
          <p className="text-2xl font-bold mt-2">{stats.invoices.pending}</p>
          <p className="text-sm text-gray-500 mt-1">{stats.invoices.overdue} overdue</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-gray-500 text-sm font-medium">Pending Payments</h3>
          <p className="text-2xl font-bold mt-2">{stats.payments.pending}</p>
        </div>
      </div>
    </div>
  );
}
