import { Bell, Search, User, X } from 'lucide-react';
import { useState } from 'react';

interface HeaderProps {
  user?: {
    name: string;
    avatar_url?: string;
  };
}

interface Notification {
  id: number;
  type: 'success' | 'warning' | 'info' | 'error';
  title: string;
  message: string;
  time: string;
  read: boolean;
}

export default function Header({ user }: HeaderProps) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: 1,
      type: 'success',
      title: 'Review Completed',
      message: 'PR #124 analysis finished with quality score 8.5/10',
      time: '5 min ago',
      read: false,
    },
    {
      id: 2,
      type: 'warning',
      title: 'Critical Issue Detected',
      message: 'Security vulnerability found in authentication module',
      time: '15 min ago',
      read: false,
    },
    {
      id: 3,
      type: 'info',
      title: 'New Pull Request',
      message: 'john_doe opened PR #125 in example-repo',
      time: '1 hour ago',
      read: true,
    },
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = (id: number) => {
    setNotifications(notifications.map(n => 
      n.id === id ? { ...n, read: true } : n
    ));
  };

  const clearAll = () => {
    setNotifications([]);
    setShowNotifications(false);
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-blue-500';
    }
  };

  return (
    <header className="h-16 bg-dark-800 border-b border-dark-700 flex items-center justify-between px-6">
      <div className="flex-1 max-w-lg">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search PRs..."
            className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-600"
            suppressHydrationWarning
          />
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-gray-400 hover:text-white rounded-lg hover:bg-dark-700 transition-colors"
            suppressHydrationWarning
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            )}
          </button>

          {/* Notification Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-96 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50">
              <div className="p-4 border-b border-dark-700 flex items-center justify-between">
                <div>
                  <h3 className="text-white font-semibold">Notifications</h3>
                  <p className="text-xs text-gray-400">{unreadCount} unread</p>
                </div>
                <button
                  onClick={clearAll}
                  className="text-xs text-primary-500 hover:text-primary-400"
                >
                  Clear all
                </button>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No notifications</p>
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      onClick={() => markAsRead(notification.id)}
                      className={`p-4 border-b border-dark-700 hover:bg-dark-700 cursor-pointer transition-colors ${
                        !notification.read ? 'bg-dark-750' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${getNotificationColor(notification.type)}`}></div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white">{notification.title}</p>
                          <p className="text-xs text-gray-400 mt-1">{notification.message}</p>
                          <p className="text-xs text-gray-500 mt-1">{notification.time}</p>
                        </div>
                        {!notification.read && (
                          <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User menu */}
        <div className="flex items-center space-x-3 cursor-pointer hover:bg-dark-700 rounded-lg px-3 py-2 transition-colors">
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name}
              className="w-8 h-8 rounded-full"
            />
          ) : (
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
          )}
          <span className="text-sm font-medium text-white">{user?.name || 'Guest'}</span>
        </div>
      </div>
    </header>
  );
}
