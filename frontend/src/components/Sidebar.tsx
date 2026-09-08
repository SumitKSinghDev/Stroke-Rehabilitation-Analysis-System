import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Settings, 
  ShieldAlert, 
  LogOut, 
  Activity, 
  UserCircle,
  BookOpen
} from 'lucide-react';
import { clearAuthToken, getStoredUser } from '../api';

interface SidebarProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ darkMode, toggleDarkMode }) => {
  const user = getStoredUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuthToken();
    navigate('/login');
  };

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, roles: ['Admin', 'Physiotherapist', 'Doctor'] },
    { to: '/patients', label: 'Patients', icon: Users, roles: ['Admin', 'Physiotherapist', 'Doctor'] },
    { to: '/methodology', label: 'Methodology', icon: BookOpen, roles: ['Admin', 'Physiotherapist', 'Doctor', 'Patient'] },
    { to: '/settings', label: 'Settings', icon: Settings, roles: ['Admin', 'Physiotherapist', 'Doctor', 'Patient'] },
  ];

  // If user is Admin, add the Admin Portal item
  if (user?.role === 'Admin') {
    navItems.splice(3, 0, { to: '/admin', label: 'Admin Portal', icon: ShieldAlert, roles: ['Admin'] });
  }

  return (
    <div className="w-64 h-screen bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col justify-between fixed left-0 top-0 z-30">
      <div>
        {/* Header Branding */}
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
            <Activity className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="font-extrabold text-slate-800 dark:text-white tracking-wide text-lg">RehabShield</h1>
            <p className="text-[10px] text-teal-500 font-semibold tracking-wider uppercase">AI Decision Support</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `
                  flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200
                  ${isActive 
                    ? 'bg-primary text-white shadow-md shadow-primary/20' 
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Footer Profile */}
      <div className="p-4 border-t border-slate-100 dark:border-slate-800">
        <div className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl mb-3">
          <div className="w-9 h-9 bg-teal-500/10 rounded-full flex items-center justify-center text-teal-600 dark:text-teal-400">
            <UserCircle className="w-6 h-6" />
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="font-semibold text-slate-800 dark:text-slate-200 text-xs truncate leading-tight">
              {user?.full_name || 'Clinician Account'}
            </h4>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium capitalize truncate">
              {user?.role || 'Physiotherapist'}
            </p>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 hover:text-red-700 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
};
export default Sidebar;
