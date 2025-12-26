'use client';

import { useState, useEffect } from 'react';
import { dashboardAPI } from '@/lib/api';
import { DashboardStats, RevenueChartData, CustomerGrowthData, PackageDistributionData } from '@/types';

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [revenueChart, setRevenueChart] = useState<RevenueChartData[]>([]);
  const [customerGrowth, setCustomerGrowth] = useState<CustomerGrowthData[]>([]);
  const [packageDistribution, setPackageDistribution] = useState<PackageDistributionData[]>([]);
  const [recentActivities, setRecentActivities] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, revenueData, growthData, distData, activitiesData] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getRevenueChart(12),
        dashboardAPI.getCustomerGrowth(12),
        dashboardAPI.getPackageDistribution(),
        dashboardAPI.getRecentActivities(5),
      ]);

      setStats(statsData);
      setRevenueChart(revenueData.data);
      setCustomerGrowth(growthData.data);
      setPackageDistribution(distData.distribution);
      setRecentActivities(activitiesData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  return {
    stats,
    revenueChart,
    customerGrowth,
    packageDistribution,
    recentActivities,
    loading,
    error,
    refresh: fetchDashboardData,
  };
}
