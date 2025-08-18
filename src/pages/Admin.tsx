import React, { useState } from 'react';
import { 
  Users, 
  Shield, 
  Settings, 
  Database, 
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Admin: React.FC = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [isLoading, setIsLoading] = useState(false);

  const tabs = [
    { id: 'users', name: 'Users', icon: Users },
    { id: 'permissions', name: 'Permissions', icon: Shield },
    { id: 'system', name: 'System', icon: Settings },
    { id: 'audit', name: 'Audit Logs', icon: Activity },
  ];

  const systemStatus = [
    { name: 'API Service', status: 'healthy', uptime: '99.9%' },
    { name: 'AI Service', status: 'healthy', uptime: '98.7%' },
    { name: 'Database', status: 'healthy', uptime: '99.8%' },
    { name: 'Storage (MinIO)', status: 'healthy', uptime: '100%' },
    { name: 'Search (Weaviate)', status: 'healthy', uptime: '99.2%' },
    { name: 'Keycloak', status: 'warning', uptime: '97.3%' },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <RefreshCw className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Administration</h1>
        <p className="text-gray-600 mt-1">Manage users, permissions, and system settings</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors
                    ${isActive
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="large" />
            </div>
          ) : (
            <>
              {/* Users Tab */}
              {activeTab === 'users' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium text-gray-900">User Management</h3>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                      Add User
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            User
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Role
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Last Active
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {[
                          { name: 'John Admin', email: 'admin@sgd.com', role: 'Administrator', status: 'Active', lastActive: '2 minutes ago' },
                          { name: 'Sarah Manager', email: 'sarah@sgd.com', role: 'Manager', status: 'Active', lastActive: '1 hour ago' },
                          { name: 'Mike User', email: 'mike@sgd.com', role: 'User', status: 'Active', lastActive: '3 hours ago' },
                          { name: 'Lisa Viewer', email: 'lisa@sgd.com', role: 'Viewer', status: 'Inactive', lastActive: '2 days ago' },
                        ].map((user, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                                  <Users className="w-5 h-5 text-gray-600" />
                                </div>
                                <div className="ml-4">
                                  <div className="text-sm font-medium text-gray-900">{user.name}</div>
                                  <div className="text-sm text-gray-500">{user.email}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                                {user.role}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                user.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                              }`}>
                                {user.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {user.lastActive}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <button className="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                              <button className="text-red-600 hover:text-red-900">Delete</button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Permissions Tab */}
              {activeTab === 'permissions' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-gray-900">Role-Based Access Control</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[
                      { role: 'Administrator', permissions: ['Full system access', 'User management', 'System configuration', 'Audit logs'] },
                      { role: 'Manager', permissions: ['Document management', 'User viewing', 'Analytics access', 'Category management'] },
                      { role: 'User', permissions: ['Upload documents', 'Search documents', 'View own documents', 'Chat with documents'] },
                      { role: 'Viewer', permissions: ['View documents', 'Search documents', 'Export documents'] }
                    ].map((roleData) => (
                      <div key={roleData.role} className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-3">{roleData.role}</h4>
                        <ul className="space-y-2">
                          {roleData.permissions.map((permission, index) => (
                            <li key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                              <CheckCircle className="w-4 h-4 text-green-500" />
                              <span>{permission}</span>
                            </li>
                          ))}
                        </ul>
                        <button className="mt-3 text-blue-600 text-sm hover:text-blue-800">
                          Edit Permissions
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* System Tab */}
              {activeTab === 'system' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-gray-900">System Status</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {systemStatus.map((service) => (
                      <div key={service.name} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{service.name}</h4>
                          {getStatusIcon(service.status)}
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(service.status)}`}>
                          {service.status}
                        </span>
                        <p className="text-sm text-gray-500 mt-2">Uptime: {service.uptime}</p>
                      </div>
                    ))}
                  </div>

                  <div className="border-t pt-6">
                    <h4 className="font-medium text-gray-900 mb-4">System Configuration</h4>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-700">Max file upload size</span>
                        <span className="text-sm font-medium">50 MB</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-700">Supported file types</span>
                        <span className="text-sm font-medium">PDF, DOC, DOCX, JPG, PNG</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-700">OCR languages</span>
                        <span className="text-sm font-medium">English, Spanish</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-700">AI processing enabled</span>
                        <span className="text-sm font-medium text-green-600">Yes</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Audit Logs Tab */}
              {activeTab === 'audit' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium text-gray-900">Audit Logs</h3>
                    <div className="flex space-x-4">
                      <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        <option>All Actions</option>
                        <option>Document Upload</option>
                        <option>Document Access</option>
                        <option>User Login</option>
                        <option>System Changes</option>
                      </select>
                      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        Export Logs
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Timestamp
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            User
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Action
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Resource
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            IP Address
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {[
                          { timestamp: '2024-01-15 14:30:25', user: 'admin@sgd.com', action: 'DOCUMENT_UPLOAD', resource: 'quarterly-report.pdf', ip: '192.168.1.100' },
                          { timestamp: '2024-01-15 14:25:10', user: 'sarah@sgd.com', action: 'DOCUMENT_ACCESS', resource: 'financial-data.xlsx', ip: '192.168.1.101' },
                          { timestamp: '2024-01-15 14:20:45', user: 'mike@sgd.com', action: 'USER_LOGIN', resource: 'N/A', ip: '192.168.1.102' },
                          { timestamp: '2024-01-15 14:15:30', user: 'admin@sgd.com', action: 'SYSTEM_CONFIG', resource: 'upload_settings', ip: '192.168.1.100' },
                        ].map((log, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {log.timestamp}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {log.user}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                                {log.action}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {log.resource}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {log.ip}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};