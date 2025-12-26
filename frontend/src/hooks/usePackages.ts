'use client';

import { useState, useEffect } from 'react';
import { packagesAPI } from '@/lib/api';
import { Package } from '@/types';

interface UsePackagesParams {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  package_type?: string;
}

export function usePackages(params: UsePackagesParams = {}) {
  const [packages, setPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState({
    total: 0,
    active: 0,
    inactive: 0,
    residential: 0,
    business: 0,
    corporate: 0,
  });

  useEffect(() => {
    fetchPackages();
    fetchCount();
  }, [params.skip, params.limit, params.is_active, params.package_type]);

  const fetchPackages = async () => {
    try {
      setLoading(true);
      const data = await packagesAPI.getList(params);
      setPackages(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch packages');
    } finally {
      setLoading(false);
    }
  };

  const fetchCount = async () => {
    try {
      const data = await packagesAPI.getCount();
      setCount(data);
    } catch (err: any) {
      console.error('Failed to fetch count:', err);
    }
  };

  const createPackage = async (data: any) => {
    const result = await packagesAPI.create(data);
    await fetchPackages();
    await fetchCount();
    return result;
  };

  const updatePackage = async (id: number, data: any) => {
    const result = await packagesAPI.update(id, data);
    await fetchPackages();
    await fetchCount();
    return result;
  };

  const deletePackage = async (id: number) => {
    await packagesAPI.delete(id);
    await fetchPackages();
    await fetchCount();
  };

  const togglePackage = async (id: number) => {
    const result = await packagesAPI.toggle(id);
    await fetchPackages();
    await fetchCount();
    return result;
  };

  return {
    packages,
    count,
    loading,
    error,
    createPackage,
    updatePackage,
    deletePackage,
    togglePackage,
    refresh: fetchPackages,
  };
}
