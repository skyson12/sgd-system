import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Upload, 
  Search, 
  BarChart3, 
  Clock, 
  CheckCircle,
  AlertCircle,
  TrendingUp
} from 'lucide-react';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

interface MetricsData {
  totalDocuments: number;
  documentsByCategory: Record<string, number>;
  documentsByStatus: Record<string, number>;
  processingStats: {
    processedLast24h: number;
    averageProcessingTime: string;
    successRate: number;
  };
  storageUsage: {
    totalSizeMb: number;
    averageFileSizeMb: number;
  };
  recentActivity: Array<{
    id: number;
    title: string;
    action: string;
    timestamp: string;
    user: string;
  }>;
}

export const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiService.getAnalytics();
      setMetrics(data);
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Dashboard</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={loadMetrics}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  const statsCards = [
    {
      title: 'Total Documents',
      value: metrics?.totalDocuments || 0,
      icon: FileText,
      color: 'bg-blue-500',
      change: '+12%'
    },
    {
      title: 'Processed Today',
      value: metrics?.processingStats.processedLast24h || 0,
      icon: CheckCircle,
      color: 'bg-green-500',
      change: '+8%'
    },
    {
      title: 'Processing Time',
      value: metrics?.processingStats.averageProcessingTime || '0s',
      icon: Clock,
      color: 'bg-yellow-500',
      change: '-15%'
    },
    {
      title: 'Success Rate',
      value: `${((metrics?.processingStats.successRate || 0) * 100).toFixed(1)}%`,
      icon: TrendingUp,
      color: 'bg-purple-500',
      change: '+2%'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome to your intelligent document management system
          </p>
        </div>
        <div className="flex space-x-4">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Upload className="w-5 h-5" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-green-600 mt-1">{stat.change} vs last week</p>
                </div>
                <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Documents by Category */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Documents by Category</h3>
          <div className="space-y-4">
            {metrics?.documentsByCategory && Object.entries(metrics.documentsByCategory).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-700 capitalize">{category || 'Uncategorized'}</span>
                </div>
                <span className="text-gray-900 font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {metrics?.recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                  <FileText className="w-5 h-5 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {activity.title}
                  </p>
                  <p className="text-sm text-gray-500">
                    {activity.action} by {activity.user}
                  </p>
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(activity.timestamp).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Storage Usage */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Storage Usage</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {metrics?.storageUsage.totalSizeMb?.toFixed(1) || '0'} MB
            </p>
            <p className="text-gray-600">Total Storage Used</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {metrics?.storageUsage.averageFileSizeMb?.toFixed(1) || '0'} MB
            </p>
            <p className="text-gray-600">Average File Size</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">
              {metrics?.totalDocuments || 0}
            </p>
            <p className="text-gray-600">Total Files</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-8 text-white">
        <h3 className="text-2xl font-bold mb-2">Ready to get started?</h3>
        <p className="text-blue-100 mb-6">
          Upload documents, search with AI, or explore your analytics
        </p>
        <div className="flex flex-wrap gap-4">
          <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center space-x-2">
            <Upload className="w-5 h-5" />
            <span>Upload Document</span>
          </button>
          <button className="bg-white bg-opacity-20 text-white border border-white border-opacity-30 px-6 py-3 rounded-lg font-medium hover:bg-opacity-30 transition-colors flex items-center space-x-2">
            <Search className="w-5 h-5" />
            <span>Search Documents</span>
          </button>
          <button className="bg-white bg-opacity-20 text-white border border-white border-opacity-30 px-6 py-3 rounded-lg font-medium hover:bg-opacity-30 transition-colors flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>View Analytics</span>
          </button>
        </div>
      </div>
    </div>
  );
};