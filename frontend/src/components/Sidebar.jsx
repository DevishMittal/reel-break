import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  ChartBarIcon, 
  CogIcon, 
  ClockIcon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
      <div className="flex-1 flex flex-col min-h-0 bg-indigo-700">
        <div className="flex items-center h-16 flex-shrink-0 px-4 bg-indigo-800">
          <div className="flex items-center space-x-2">
            <ClockIcon className="h-8 w-8 text-white" />
            <span className="text-white text-xl font-semibold">ReelBreak</span>
          </div>
        </div>
        <div className="flex-1 flex flex-col overflow-y-auto">
          <nav className="flex-1 px-2 py-4 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  ${location.pathname === item.href ? 'bg-indigo-800 text-white' : 'text-indigo-100 hover:bg-indigo-600'}
                  group flex items-center px-2 py-2 text-base font-medium rounded-md
                `}
              >
                <item.icon className="mr-4 h-6 w-6 text-indigo-200" aria-hidden="true" />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;