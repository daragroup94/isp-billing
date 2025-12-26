// hooks/useCustomers.ts
import { useState, useEffect } from 'react';
import { customerApi } from '@/lib/api';
import type { Customer, CustomerFilters } from '@/types';

export function useCustomers(filters?: CustomerFilters) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const data = await customerApi.getAll(filters);
      setCustomers(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch customers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [JSON.stringify(filters)]);

  const createCustomer = async (data: Partial<Customer>) => {
    try {
      const newCustomer = await customerApi.create(data);
      setCustomers([newCustomer, ...customers]);
      return newCustomer;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create customer');
    }
  };

  const updateCustomer = async (id: number, data: Partial<Customer>) => {
    try {
      const updated = await customerApi.update(id, data);
      setCustomers(customers.map(c => c.id === id ? updated : c));
      return updated;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to update customer');
    }
  };

  const deleteCustomer = async (id: number) => {
    try {
      await customerApi.delete(id);
      setCustomers(customers.filter(c => c.id !== id));
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to delete customer');
    }
  };

  const suspendCustomer = async (id: number) => {
    try {
      const updated = await customerApi.suspend(id);
      setCustomers(customers.map(c => c.id === id ? updated : c));
      return updated;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to suspend customer');
    }
  };

  const activateCustomer = async (id: number) => {
    try {
      const updated = await customerApi.activate(id);
      setCustomers(customers.map(c => c.id === id ? updated : c));
      return updated;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to activate customer');
    }
  };

  return {
    customers,
    loading,
    error,
    refetch: fetchCustomers,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    suspendCustomer,
    activateCustomer,
  };
}

export function useCustomer(id: number) {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCustomer = async () => {
      try {
        setLoading(true);
        const data = await customerApi.getById(id);
        setCustomer(data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch customer');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchCustomer();
    }
  }, [id]);

  return { customer, loading, error };
}
