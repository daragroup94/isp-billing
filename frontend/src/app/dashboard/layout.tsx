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
      <aside className="w-64 bg-white border-r">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">ISP Billing</h1>
        </div>
        <nav className="p-4">
          <Link href="/dashboard" className="block px-4 py-2 rounded-lg hover:bg-blue-50">
            Dashboard
          </Link>
        </nav>
        <div className="absolute bottom-0 w-64 p-4 border-t">
          <p className="text-sm font-medium">{user.full_name}</p>
          <button onClick={logout} className="text-sm text-red-600 mt-2">
            Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
