import CustomerList from '@/components/customers/CustomerList';

export default function CustomersPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded shadow-sm transition-colors">
          Add Customer
        </button>
      </div>
      
      <CustomerList />
    </div>
  );
}
