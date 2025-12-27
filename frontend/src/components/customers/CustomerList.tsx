'use client';

import { useCustomers } from '@/hooks/useCustomers';
import { formatCurrency } from '@/lib/utils';
import type { Customer } from '@/types';

export default function CustomerList() {
  const { customers, loading, error, deleteCustomer, suspendCustomer, activateCustomer } = useCustomers();

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete customer "${name}"?`)) return;
    try {
      await deleteCustomer(id);
      alert('Customer deleted successfully');
    } catch (err: any) {
      alert(err.message || 'Failed to delete customer');
    }
  };

  const handleStatusChange = async (id: number, currentStatus: string) => {
    try {
      if (currentStatus === 'active') {
        await suspendCustomer(id);
        alert('Customer suspended');
      } else {
        await activateCustomer(id);
        alert('Customer activated');
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
        {error}
      </div>
    );
  }

  if (customers.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow-sm border">
        <p className="text-gray-500 text-lg">No customers found.</p>
        <p className="text-gray-400 text-sm mt-2">Create your first customer to get started.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Package</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {customers.map((customer) => (
              <tr key={customer.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                      <div className="text-sm text-gray-500">#{customer.customer_number}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{customer.email}</div>
                  <div className="text-sm text-gray-500">{customer.phone}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{customer.package?.name || 'No Package'}</div>
                  <div className="text-sm text-gray-500">
                    {customer.package ? formatCurrency(customer.package.price) : '-'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    customer.status === 'active' ? 'bg-green-100 text-green-800' :
                    customer.status === 'suspended' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {customer.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <button
                    onClick={() => handleStatusChange(customer.id, customer.status)}
                    className={`${
                      customer.status === 'active' ? 'text-yellow-600 hover:text-yellow-900' : 'text-green-600 hover:text-green-900'
                    }`}
                  >
                    {customer.status === 'active' ? 'Suspend' : 'Activate'}
                  </button>
                  <button
                    onClick={() => handleDelete(customer.id, customer.name)}
                    className="text-red-600 hover:text-red-900 ml-4"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
