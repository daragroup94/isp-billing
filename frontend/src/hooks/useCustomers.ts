'use client';

import { useState, useEffect } from 'react';
import { customersAPI } from '@/lib/api';
import { Customer } from '@/types';

interface UseCustomersParams {
  skip?: number;
  limit?: number;
  search?: string;
  status?: string;
  package_id?: number;
}

export function useCustomers(params: UseCustomersParams = {}) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState({
    total: 0,
    active: 0,
    suspended: 0,
    inactive: 0,
    terminated: 0,
  });

  useEffect(() => {
    fetchCustomers();
    fetchCount();
  }, [params.skip, params.limit, params.search, params.status, params.package_id]);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const data = await customersAPI.getList(params);
      setCustomers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch customers');
    } finally {
      setLoading(false);
    }
  };

  const fetchCount = async () => {
    try {
      const data = await customersAPI.getCount(params.status);
      setCount(data);
    } catch (err: any) {
      console.error('Failed to fetch count:', err);
    }
  };

  const createCustomer = async (data: any) => {
    const result = await customersAPI.create(data);
    await fetchCustomers();
    await fetchCount();
    return result;
  };

  const updateCustomer = async (id: number, data: any) => {
    const result = await customersAPI.update(id, data);
    await fetchCustomers();
    await fetchCount();
    return result;
  };

  const deleteCustomer = async (id: number) => {
    await customersAPI.delete(id);
    await fetchCustomers();
    await fetchCount();
  };

  const suspendCustomer = async (id: number) => {
    const result = await customersAPI.suspend(id);
    await fetchCustomers();
    await fetchCount();
    return result;
  };

  const activateCustomer = async (id: number) => {
    const result = await customersAPI.activate(id);
    await fetchCustomers();
    await fetchCount();
    return result;
  };

  return {
    customers,
    count,
    loading,
    error,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    suspendCustomer,
    activateCustomer,
    refresh: fetchCustomers,
  };
}
