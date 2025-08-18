'use client'

import React from 'react'
import { FileText, Upload, Search, BarChart3 } from 'lucide-react'

export function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <FileText className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SGD System</h1>
              <p className="text-gray-600">Intelligent Document Management</p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { title: 'Total Documents', value: '1,247', icon: FileText, color: 'bg-blue-500' },
            { title: 'Processed Today', value: '23', icon: Upload, color: 'bg-green-500' },
            { title: 'Pending Review', value: '8', icon: Search, color: 'bg-yellow-500' },
            { title: 'Success Rate', value: '98.4%', icon: BarChart3, color: 'bg-purple-500' }
          ].map((stat, index) => {
            const Icon = stat.icon
            return (
              <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Quick Actions */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-8 text-white">
          <h3 className="text-2xl font-bold mb-2">System Status</h3>
          <p className="text-blue-100 mb-6">
            All services are running and ready for document processing
          </p>
          <div className="flex flex-wrap gap-4">
            <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors">
              Upload Document
            </button>
            <button className="bg-white bg-opacity-20 text-white border border-white border-opacity-30 px-6 py-3 rounded-lg font-medium hover:bg-opacity-30 transition-colors">
              Search Documents
            </button>
            <button className="bg-white bg-opacity-20 text-white border border-white border-opacity-30 px-6 py-3 rounded-lg font-medium hover:bg-opacity-30 transition-colors">
              View Analytics
            </button>
          </div>
        </div>

        {/* Service Status */}
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: 'API Service', status: 'healthy' },
              { name: 'AI Service', status: 'healthy' },
              { name: 'Database', status: 'healthy' },
              { name: 'Storage (MinIO)', status: 'healthy' },
              { name: 'Search (Weaviate)', status: 'healthy' },
              { name: 'Keycloak', status: 'healthy' }
            ].map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-700">{service.name}</span>
                <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                  {service.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}