import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  ChatBubbleBottomCenterTextIcon,
  MagnifyingGlassIcon,
  InformationCircleIcon,
  Bars3Icon,
  XMarkIcon,
  CpuChipIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Chat', href: '/', icon: ChatBubbleBottomCenterTextIcon },
  { name: 'Search Funds', href: '/search', icon: MagnifyingGlassIcon },
  { name: 'About', href: '/about', icon: InformationCircleIcon },
]

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const isActivePath = (path: string) => {
    return location.pathname === path
  }

  return (
    <div className="min-h-screen bg-[#0B1120]">
      {/* Mobile menu */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-[#0B1120]/95 backdrop-blur-xl shadow-2xl border-r border-white/10">
          <div className="flex h-16 shrink-0 items-center justify-between px-4 border-b border-white/10">
            <div className="flex items-center">
              <div className="relative">
                <CpuChipIcon className="h-8 w-8 text-purple-400" />
                <SparklesIcon className="h-4 w-4 text-purple-300 absolute -top-1 -right-1 animate-pulse" />
              </div>
              <span className="ml-2 text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                MF Agent
              </span>
            </div>
            <button
              type="button"
              className="text-gray-400 hover:text-white transition-colors"
              onClick={() => setSidebarOpen(false)}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex flex-1 flex-col p-4">
            <ul className="space-y-2">
              {navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`
                      group flex items-center px-3 py-2.5 text-sm font-medium rounded-xl transition-all duration-300
                      ${isActivePath(item.href)
                        ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-white shadow-lg shadow-purple-500/20 border border-purple-500/30'
                        : 'text-gray-300 hover:bg-white/5 hover:text-white hover:border hover:border-white/10'
                      }
                    `}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <item.icon className={`mr-3 h-5 w-5 transition-transform group-hover:scale-110 ${isActivePath(item.href) ? 'text-purple-400' : ''}`} />
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-1 flex-col min-h-0 bg-[#0B1120]/95 backdrop-blur-xl border-r border-white/10">
          <div className="flex h-16 shrink-0 items-center px-4 border-b border-white/10">
            <div className="relative">
              <CpuChipIcon className="h-8 w-8 text-purple-400" />
              <SparklesIcon className="h-4 w-4 text-purple-300 absolute -top-1 -right-1 animate-pulse" />
            </div>
            <span className="ml-2 text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              MF Agent
            </span>
          </div>
          <nav className="flex-1 p-4">
            <ul className="space-y-2">
              {navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`
                      group flex items-center px-3 py-2.5 text-sm font-medium rounded-xl transition-all duration-300
                      ${isActivePath(item.href)
                        ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-white shadow-lg shadow-purple-500/20 border border-purple-500/30'
                        : 'text-gray-300 hover:bg-white/5 hover:text-white hover:border hover:border-white/10'
                      }
                    `}
                  >
                    <item.icon className={`mr-3 h-5 w-5 transition-transform group-hover:scale-110 ${isActivePath(item.href) ? 'text-purple-400' : ''}`} />
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          
          {/* Footer */}
          <div className="p-4 border-t border-white/10">
            <div className="text-xs text-gray-400 text-center">
              <p className="flex items-center justify-center gap-1">
                <SparklesIcon className="h-3 w-3 text-purple-400" />
                AI-Powered Investment Assistant
              </p>
              <p className="mt-1 text-gray-500">Version 1.0.0</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar with glassmorphism */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-white/10 bg-[#0B1120]/80 backdrop-blur-xl px-4 shadow-lg sm:px-6 lg:px-8">
          <button
            type="button"
            className="lg:hidden text-gray-400 hover:text-white transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1 items-center">
              <h1 className="text-lg font-semibold text-white">
                {navigation.find(item => isActivePath(item.href))?.name || 'Mutual Funds Agent'}
              </h1>
              <span className="ml-3 px-2 py-0.5 text-[10px] font-medium bg-yellow-500/20 text-yellow-300 rounded-full border border-yellow-500/30">
                BETA
              </span>
            </div>
            
            {/* Status indicator */}
            <div className="flex items-center gap-x-2">
              <div className="flex items-center">
                <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50"></div>
                <span className="ml-2 text-sm text-gray-400">Online</span>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  )
}
