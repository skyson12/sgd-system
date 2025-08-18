import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, FileText, Clock, Users, Activity } from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Analytics: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    // Simulate loading analytics data
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  }, [timeRange]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Document management insights and statistics</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900">1,247</p>
              <p className="text-sm text-green-600 mt-1">+12.5% vs last period</p>
            </div>
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Processing Time</p>
              <p className="text-2xl font-bold text-gray-900">2.3s</p>
              <p className="text-sm text-green-600 mt-1">-15% vs last period</p>
            </div>
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Active Users</p>
              <p className="text-2xl font-bold text-gray-900">84</p>
              <p className="text-sm text-blue-600 mt-1">+8% vs last period</p>
            </div>
            <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">98.4%</p>
              <p className="text-sm text-green-600 mt-1">+2.1% vs last period</p>
            </div>
            <div className="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Document Upload Trends */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Document Upload Trends</h3>
          <div className="h-64 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-4" />
              <p>Chart visualization would be implemented here</p>
              <p className="text-sm">Using libraries like Recharts or Chart.js</p>
            </div>
          </div>
        </div>

        {/* Category Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Category Distribution</h3>
          <div className="space-y-4">
            {[
              { name: 'Financial', count: 324, percentage: 26 },
              { name: 'Legal', count: 298, percentage: 24 },
              { name: 'Technical', count: 245, percentage: 20 },
              { name: 'Administrative', count: 186, percentage: 15 },
              { name: 'Marketing', count: 124, percentage: 10 },
              { name: 'Other', count: 70, percentage: 5 }
            ].map((category) => (
              <div key={category.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-700">{category.name}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${category.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-gray-600 text-sm w-12 text-right">{category.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Processing Performance */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Processing Performance</h3>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>OCR Accuracy</span>
                <span>96.8%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '96.8%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Classification Accuracy</span>
                <span>94.2%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '94.2%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Processing Speed</span>
                <span>89.5%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '89.5%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* User Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent User Activity</h3>
          <div className="space-y-4">
            {[
              { user: 'Sarah Johnson', action: 'Uploaded 3 documents', time: '2 hours ago' },
              { user: 'Mike Chen', action: 'Performed semantic search', time: '3 hours ago' },
              { user: 'Emily Davis', action: 'Updated document classification', time: '5 hours ago' },
              { user: 'John Smith', action: 'Downloaded quarterly report', time: '1 day ago' },
              { user: 'Lisa Brown', action: 'Created new category', time: '1 day ago' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                  <Activity className="w-5 h-5 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {activity.user}
                  </p>
                  <p className="text-sm text-gray-500">
                    {activity.action}
                  </p>
                </div>
                <span className="text-xs text-gray-400">
                  {activity.time}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Storage Analytics */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Storage Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-24 h-24 mx-auto bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-blue-600">2.4GB</span>
            </div>
            <p className="text-gray-600">Total Storage Used</p>
          </div>
          
          <div className="text-center">
            <div className="w-24 h-24 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-green-600">1.9MB</span>
            </div>
            <p className="text-gray-600">Average File Size</p>
          </div>
          
          <div className="text-center">
            <div className="w-24 h-24 mx-auto bg-purple-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-purple-600">47%</span>
            </div>
            <p className="text-gray-600">Storage Efficiency</p>
          </div>
        </div>
      </div>
    </div>
  );
};