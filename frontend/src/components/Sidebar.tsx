import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FolderGit2,
  Sparkles,
  Settings,
  HelpCircle,
  Brain,
  BarChart,
  Wand2,
} from 'lucide-react';
import clsx from 'clsx';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Repositories', href: '/repositories', icon: FolderGit2 },
  { name: 'AI Insights', href: '/insights', icon: Sparkles },
  { name: 'ML Training', href: '/ml-training', icon: Brain, badge: 'New' },
  { name: 'Analytics', href: '/analytics', icon: BarChart, badge: 'New' },
  { name: 'Code Fixes', href: '/code-fixes', icon: Wand2, badge: 'New' },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Help', href: '/help', icon: HelpCircle },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-64 bg-dark-800 border-r border-dark-700 flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-dark-700">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white">AI-Powered</h1>
            <p className="text-xs text-gray-400">Code Review System</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-300 hover:bg-dark-700 hover:text-white'
              )}
            >
              <div className="flex items-center space-x-3">
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-xs font-semibold bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-dark-700">
        <div className="text-xs text-gray-500">
          Version 2.0.0 • Advanced Features
        </div>
      </div>
    </aside>
  );
}
