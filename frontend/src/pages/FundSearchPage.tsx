import { useState } from 'react'
import { MagnifyingGlassIcon, ChartBarIcon, InformationCircleIcon } from '@heroicons/react/24/outline'
import { apiClient, type FundSearchRequest } from '../utils/api'
import { getErrorMessage, formatCurrency, formatPercentage } from '../utils'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

interface Fund {
  scheme_name?: string
  fund_name?: string
  amc_name?: string
  nav?: string | number
  nav_date?: string
  return_1m?: string | number
  return_ytd?: string | number
  return_1y?: string | number
  return_3y?: string | number
  expense_ratio?: string | number
  fund_manager?: string
  sebi_risk_category?: string
  scheme_code?: string
  isin?: string
  url?: string
  title?: string
  content?: string
}

export default function FundSearchPage() {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState('general')
  const [results, setResults] = useState<Fund[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const searchTypes = [
    { value: 'general', label: 'General Search' },
    { value: 'nav', label: 'NAV Information' },
    { value: 'performance', label: 'Performance Data' },
    { value: 'fund_manager', label: 'Fund Manager' },
    { value: 'expense_ratio', label: 'Expense Ratio' },
    { value: 'risk', label: 'Risk Category' }
  ]

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!query.trim()) {
      toast.error('Please enter a fund name to search')
      return
    }

    setIsLoading(true)
    setError(null)
    setHasSearched(true)

    try {
      const searchRequest: FundSearchRequest = {
        fund_name: query.trim(),
        search_type: searchType
      }

      const response = await apiClient.searchFunds(searchRequest)

      if (response.found && response.results) {
        setResults(response.results)
        toast.success(`Found ${response.results.length} result(s)`)
      } else {
        setResults([])
        toast.error(response.error || 'No funds found matching your search')
      }
    } catch (error) {
      const errorMessage = getErrorMessage(error)
      setError(errorMessage)
      setResults([])
      toast.error(`Search failed: ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }

  const clearSearch = () => {
    setQuery('')
    setResults([])
    setError(null)
    setHasSearched(false)
  }

  const renderFundCard = (fund: Fund, index: number) => {
    const fundName = fund.scheme_name || fund.fund_name || fund.title || 'Unknown Fund'
    const amcName = fund.amc_name || 'Unknown AMC'
    
    return (
      <div key={index} className="group card hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 hover:scale-[1.02]">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-purple-300 transition-colors">
              {fundName}
            </h3>
            <p className="text-sm text-gray-400">{amcName}</p>
          </div>
          
          {fund.sebi_risk_category && (
            <span className="px-3 py-1 text-xs font-medium bg-yellow-500/20 text-yellow-300 rounded-full border border-yellow-500/30">
              {fund.sebi_risk_category}
            </span>
          )}
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {fund.nav && (
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">NAV</p>
              <p className="text-sm font-semibold text-white">
                {typeof fund.nav === 'number' ? formatCurrency(fund.nav) : `₹${fund.nav}`}
              </p>
              {fund.nav_date && <p className="text-xs text-gray-500">{fund.nav_date}</p>}
            </div>
          )}
          
          {fund.return_1y && (
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">1Y Return</p>
              <p className={`text-sm font-semibold ${
                parseFloat(fund.return_1y.toString()) >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {typeof fund.return_1y === 'number' ? formatPercentage(fund.return_1y) : `${fund.return_1y}%`}
              </p>
            </div>
          )}
          
          {fund.expense_ratio && (
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">Expense Ratio</p>
              <p className="text-sm font-semibold text-white">{fund.expense_ratio}%</p>
            </div>
          )}
          
          {fund.fund_manager && (
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">Fund Manager</p>
              <p className="text-sm font-semibold text-white">{fund.fund_manager}</p>
            </div>
          )}
        </div>

        {/* Performance metrics */}
        {(fund.return_1m || fund.return_ytd || fund.return_3y) && (
          <div className="border-t border-white/10 pt-3">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Performance</p>
            <div className="grid grid-cols-3 gap-4">
              {fund.return_1m && (
                <div>
                  <p className="text-xs text-gray-500">1M</p>
                  <p className={`text-sm font-medium ${
                    parseFloat(fund.return_1m.toString()) >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {fund.return_1m}%
                  </p>
                </div>
              )}
              
              {fund.return_ytd && (
                <div>
                  <p className="text-xs text-gray-500">YTD</p>
                  <p className={`text-sm font-medium ${
                    parseFloat(fund.return_ytd.toString()) >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {fund.return_ytd}%
                  </p>
                </div>
              )}
              
              {fund.return_3y && (
                <div>
                  <p className="text-xs text-gray-500">3Y</p>
                  <p className={`text-sm font-medium ${
                    parseFloat(fund.return_3y.toString()) >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {fund.return_3y}%
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Web search result content */}
        {fund.content && (
          <div className="border-t border-white/10 pt-3 mt-3">
            <p className="text-sm text-gray-300 line-clamp-3">{fund.content}</p>
            {fund.url && (
              <a 
                href={fund.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs text-purple-400 hover:text-purple-300 mt-1 inline-block transition-colors"
              >
                Read more →
              </a>
            )}
          </div>
        )}

        {/* Additional info */}
        <div className="flex justify-between items-center mt-4 pt-3 border-t border-white/10">
          <div className="text-xs text-gray-500">
            {fund.scheme_code && `Code: ${fund.scheme_code}`}
            {fund.isin && ` • ISIN: ${fund.isin}`}
          </div>
          
          <button className="btn-secondary text-xs py-1.5 px-3">
            View Details
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 min-h-screen">
      {/* Header with gradient */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
          Search Mutual Funds
        </h1>
        <p className="text-gray-400">
          Search for mutual funds by name and get detailed information including NAV, performance, and more.
        </p>
      </div>

      {/* Search Form with glassmorphism */}
      <div className="card mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="fund-search" className="block text-sm font-medium text-gray-300 mb-2">
                Fund Name
              </label>
              <input
                id="fund-search"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., SBI Bluechip Fund, HDFC Top 100, Axis Long Term..."
                className="input-field"
                disabled={isLoading}
              />
            </div>
            
            <div className="sm:w-48">
              <label htmlFor="search-type" className="block text-sm font-medium text-gray-300 mb-2">
                Search Type
              </label>
              <select
                id="search-type"
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                className="input-field"
                disabled={isLoading}
              >
                {searchTypes.map(type => (
                  <option key={type.value} value={type.value} className="bg-[#161C33] text-white">
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="btn-primary disabled:opacity-40 disabled:cursor-not-allowed flex items-center"
            >
              {isLoading ? (
                <LoadingSpinner size="small" className="mr-2" />
              ) : (
                <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
              )}
              {isLoading ? 'Searching...' : 'Search'}
            </button>
            
            {(query || hasSearched) && (
              <button
                type="button"
                onClick={clearSearch}
                className="btn-secondary"
                disabled={isLoading}
              >
                Clear
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 backdrop-blur-xl border border-red-500/30 rounded-xl">
          <div className="flex">
            <div className="flex-shrink-0">
              <InformationCircleIcon className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {hasSearched && !isLoading && (
        <div>
          {results.length > 0 ? (
            <>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  Search Results <span className="text-gray-400">({results.length})</span>
                </h2>
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg">
                  <ChartBarIcon className="w-4 h-4 text-purple-400" />
                  <span className="text-sm text-gray-300">Fund data</span>
                </div>
              </div>
              
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {results.map((fund, index) => renderFundCard(fund, index))}
              </div>
            </>
          ) : (
            <div className="text-center py-16 card">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                <MagnifyingGlassIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No funds found</h3>
              <p className="text-gray-400 mb-6">
                Try adjusting your search terms or search type.
              </p>
              <button
                onClick={() => setQuery('')}
                className="btn-primary"
              >
                Try New Search
              </button>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-16">
          <LoadingSpinner size="large" className="mx-auto mb-4" />
          <p className="text-gray-400">Searching for funds...</p>
        </div>
      )}

      {/* Initial State */}
      {!hasSearched && !isLoading && (
        <div className="text-center py-16">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <MagnifyingGlassIcon className="w-10 h-10 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Ready to search</h3>
          <p className="text-gray-400 mb-8 max-w-md mx-auto">
            Enter a fund name above to search our comprehensive database of mutual funds.
          </p>
          
          {/* Popular searches */}
          <div className="max-w-2xl mx-auto">
            <p className="text-sm text-gray-500 mb-3">Popular searches:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {['SBI Bluechip', 'HDFC Top 100', 'Axis Long Term', 'ICICI Prudential', 'Mirae Asset'].map((term) => (
                <button
                  key={term}
                  onClick={() => {
                    setQuery(term)
                    const syntheticEvent = { preventDefault: () => {} } as React.FormEvent
                    handleSearch(syntheticEvent)
                  }}
                  className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-purple-500/30 
                           rounded-lg text-sm text-gray-300 hover:text-white transition-all duration-200"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
