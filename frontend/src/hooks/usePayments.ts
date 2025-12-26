'use client';

import { useState, useEffect } from 'react';
import { paymentsAPI } from '@/lib/api';
import { Payment } from '@/types';

interface UsePaymentsParams {
  skip?: number;
  limit?: number;
  customer_id?: number;
  invoice_id?: number;
  status?: string;
  payment_method?: string;
}

export function usePayments(params: UsePaymentsParams = {}) {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState({
    total: 0,
    pending: 0,
    verified: 0,
    rejected: 0,
    cancelled: 0,
    total_verified_amount: 0,
    pending_amount: 0,
  });

  useEffect(() => {
    fetchPayments();
    fetchCount();
  }, [params.skip, params.limit, params.customer_id, params.invoice_id, params.status, params.payment_method]);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const data = await paymentsAPI.getList(params);
      setPayments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch payments');
    } finally {
      setLoading(false);
    }
  };

  const fetchCount = async () => {
    try {
      const data = await paymentsAPI.getCount();
      setCount(data);
    } catch (err: any) {
      console.error('Failed to fetch count:', err);
    }
  };

  const createPayment = async (data: any) => {
    const result = await paymentsAPI.create(data);
    await fetchPayments();
    await fetchCount();
    return result;
  };

  const verifyPayment = async (id: number, admin_notes?: string) => {
    const result = await paymentsAPI.verify(id, admin_notes);
    await fetchPayments();
    await fetchCount();
    return result;
  };

  const rejectPayment = async (id: number, rejection_reason: string, admin_notes?: string) => {
    const result = await paymentsAPI.reject(id, rejection_reason, admin_notes);
    await fetchPayments();
    await fetchCount();
    return result;
  };

  const cancelPayment = async (id: number) => {
    const result = await paymentsAPI.cancel(id);
    await fetchPayments();
    await fetchCount();
    return result;
  };

  return {
    payments,
    count,
    loading,
    error,
    createPayment,
    verifyPayment,
    rejectPayment,
    cancelPayment,
    refresh: fetchPayments,
  };
}
