import React, { useState } from 'react';
import { Search as SearchIcon, Filter, Sparkles, FileText, Eye, MessageCircle } from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Search: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [semanticSearch, setSemanticSearch] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      // Simulate API call
      setTimeout(() => {
        setResults([
          {
            id: 1,
            title: 'Q4 Financial Report',
            excerpt: 'Comprehensive analysis of financial performance for Q4 2024, showing strong revenue growth...',
            category: 'Financial',
            relevanceScore: 0.95,
            lastModified: '2024-01-15'
          },
          {
            id: 2,
            title: 'Marketing Strategy Document',
            excerpt: 'Strategic planning document outlining marketing initiatives for the upcoming quarter...',
            category: 'Marketing',
            relevanceScore: 0.87,
            lastModified: '2024-01-10'
          }
        ]);
        setIsLoading(false);
      }, 1500);
    } catch (error) {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Search Documents</h1>
        <p className="text-gray-600 mt-1">Find documents using text or semantic search</p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search for documents, content, or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={!searchQuery.trim() || isLoading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isLoading ? <LoadingSpinner size="small" /> : <SearchIcon className="w-5 h-5" />}
              <span>Search</span>
            </button>
          </div>

          {/* Search Options */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={semanticSearch}
                  onChange={(e) => setSemanticSearch(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 flex items-center space-x-1">
                  <Sparkles className="w-4 h-4" />
                  <span>Semantic Search</span>
                </span>
              </label>
              <span className="text-xs text-gray-500">
                AI-powered search that understands context and meaning
              </span>
            </div>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="border-t pt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">All Categories</option>
                  <option value="financial">Financial</option>
                  <option value="legal">Legal</option>
                  <option value="marketing">Marketing</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">All Dates</option>
                  <option value="last-week">Last Week</option>
                  <option value="last-month">Last Month</option>
                  <option value="last-year">Last Year</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">File Type</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                  <option value="">All Types</option>
                  <option value="pdf">PDF</option>
                  <option value="doc">Word Documents</option>
                  <option value="image">Images</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Search Results */}
      {isLoading ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <LoadingSpinner size="large" />
              <p className="text-gray-600 mt-4">
                {semanticSearch ? 'Performing semantic search...' : 'Searching documents...'}
              </p>
            </div>
          </div>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-gray-600">
              Found {results.length} result{results.length !== 1 ? 's' : ''} for "{searchQuery}"
            </p>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <span>Sort by:</span>
              <select className="border border-gray-300 rounded px-2 py-1">
                <option>Relevance</option>
                <option>Date Modified</option>
                <option>Title</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            {results.map((result) => (
              <div key={result.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <h3 className="text-lg font-medium text-blue-600 hover:text-blue-800 cursor-pointer">
                        {result.title}
                      </h3>
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                        {result.category}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-3">
                      {result.excerpt}
                    </p>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <span>Modified: {new Date(result.lastModified).toLocaleDateString()}</span>
                      {semanticSearch && (
                        <div className="flex items-center space-x-1">
                          <Sparkles className="w-4 h-4" />
                          <span>Relevance: {(result.relevanceScore * 100).toFixed(0)}%</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg">
                      <Eye className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg">
                      <MessageCircle className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : searchQuery && !isLoading ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <SearchIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
            <p className="text-gray-600 mb-4">
              We couldn't find any documents matching "{searchQuery}"
            </p>
            <p className="text-gray-500 text-sm">
              Try different keywords or enable semantic search for better results
            </p>
          </div>
        </div>
      ) : null}

      {/* Search Tips */}
      {!searchQuery && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Search Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Text Search</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Search for specific keywords or phrases</li>
                <li>• Use quotes for exact matches: "quarterly report"</li>
                <li>• Combine terms with AND, OR operators</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2 flex items-center space-x-1">
                <Sparkles className="w-4 h-4" />
                <span>Semantic Search</span>
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Search by meaning and context</li>
                <li>• Ask questions: "What are our Q4 sales figures?"</li>
                <li>• Find related concepts automatically</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};