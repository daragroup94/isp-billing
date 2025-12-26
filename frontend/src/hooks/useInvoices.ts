'use client';

import { useState, useEffect } from 'react';
import { invoicesAPI } from '@/lib/api';
import { Invoice } from '@/types';

interface UseInvoicesParams {
  skip?: number;
  limit?: number;
  customer_id?: number;
  status?: string;
  month?: string;
}

export function useInvoices(params: UseInvoicesParams = {}) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState({
    total: 0,
    pending: 0,
    paid: 0,
    partial: 0,
    overdue: 0,
    cancelled: 0,
    total_outstanding: 0,
    total_paid: 0,
  });

  useEffect(() => {
    fetchInvoices();
    fetchCount();
  }, [params.skip, params.limit, params.customer_id, params.status, params.month]);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const data = await invoicesAPI.getList(params);
      setInvoices(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch invoices');
    } finally {
      setLoading(false);
    }
  };

  const fetchCount = async () => {
    try {
      const data = await invoicesAPI.getCount();
      setCount(data);
    } catch (err: any) {
      console.error('Failed to fetch count:', err);
    }
  };

  const createInvoice = async (data: any) => {
    const result = await invoicesAPI.create(data);
    await fetchInvoices();
    await fetchCount();
    return result;
  };

  const generateInvoice = async (customer_id: number, billing_month: string) => {
    const result = await invoicesAPI.generate({ customer_id, billing_month });
    await fetchInvoices();
    await fetchCount();
    return result;
  };

  const updateInvoice = async (id: number, data: any) => {
    const result = await invoicesAPI.update(id, data);
    await fetchInvoices();
    await fetchCount();
    return result;
  };

  const cancelInvoice = async (id: number) => {
    const result = await invoicesAPI.cancel(id);
    await fetchInvoices();
    await fetchCount();
    return result;
  };

  const markPaid = async (id: number) => {
    const result = await invoicesAPI.markPaid(id);
    await fetchInvoices();
    await fetchCount();
    return result;
  };

  return {
    invoices,
    count,
    loading,
    error,
    createInvoice,
    generateInvoice,
    updateInvoice,
    cancelInvoice,
    markPaid,
    refresh: fetchInvoices,
  };
}
