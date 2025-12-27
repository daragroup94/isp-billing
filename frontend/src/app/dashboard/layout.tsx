'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar / Menu Navigasi */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">ISP Billing</h1>
        </div>
        
        {/* Area Menu */}
        <nav className="p-4 flex-1 space-y-1">
          <Link 
            href="/dashboard" 
            className="block px-4 py-2 rounded-lg hover:bg-blue-50 text-gray-700 font-medium"
          >
            Dashboard
          </Link>
          
          <Link 
            href="/dashboard/customers" 
            className="block px-4 py-2 rounded-lg hover:bg-blue-50 text-gray-700 font-medium"
          >
            Customers
          </Link>

          <Link 
            href="/dashboard/packages" 
            className="block px-4 py-2 rounded-lg hover:bg-blue-50 text-gray-700 font-medium"
          >
            Packages
          </Link>

          <Link 
            href="/dashboard/invoices" 
            className="block px-4 py-2 rounded-lg hover:bg-blue-50 text-gray-700 font-medium"
          >
            Invoices
          </Link>

          <Link 
            href="/dashboard/payments" 
            className="block px-4 py-2 rounded-lg hover:bg-blue-50 text-gray-700 font-medium"
          >
            Payments
          </Link>
        </nav>

        {/* Area Logout Bawah */}
        <div className="p-4 border-t bg-gray-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-bold text-gray-900">{user.full_name}</p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>
            <button 
              onClick={logout} 
              className="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-1 rounded hover:bg-red-50"
            >
              Logout
            </button>
          </div>
        </div>
      </aside>
      
      {/* Konten Utama */}
      <main className="flex-1 p-6 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
