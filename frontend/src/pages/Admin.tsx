import React, { useEffect, useState } from 'react';
import { 
  ShieldAlert, 
  Users, 
  FileText, 
  Trash2, 
  UserCheck, 
  Cpu, 
  RefreshCw,
  Clock,
  KeyRound,
  FileSpreadsheet
} from 'lucide-react';
import { api, User, AdminStats } from '../api';

export const Admin: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [statsData, usersData] = await Promise.all([
        api.admin.getStats(),
        api.admin.listUsers()
      ]);
      setStats(statsData);
      setUsers(usersData);
    } catch (err: any) {
      setError(err.message || 'Access Denied. Administrator rights required.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdateRole = async (userId: string, newRole: string) => {
    setActionLoading(userId);
    try {
      await api.admin.updateUserRole(userId, newRole);
      await loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to update user role.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteUser = async (userId: string, username: string) => {
    if (window.confirm(`Are you sure you want to permanently delete user account: ${username}?`)) {
      setActionLoading(userId);
      try {
        await api.admin.deleteUser(userId);
        await loadData();
      } catch (err: any) {
        alert(err.message || 'Failed to delete user.');
      } finally {
        setActionLoading(null);
      }
    };
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded-xl w-48 mb-8"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
          ))}
        </div>
        <div className="h-96 bg-slate-200 dark:bg-slate-800 rounded-2xl mt-8"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-rose-500/10 border border-rose-500/20 text-rose-500 p-6 rounded-2xl flex items-center space-x-3 max-w-2xl mx-auto mt-12">
        <ShieldAlert className="w-6 h-6 flex-shrink-0" />
        <div>
          <h4 className="font-extrabold text-sm">Access Restrictions</h4>
          <p className="text-xs text-rose-600/80 dark:text-rose-400/80 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 font-sans">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight">Admin Control Panel</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Clinic staff accounts, diagnostic counts, and HIPAA security logs.
          </p>
        </div>
        <button
          onClick={() => { setLoading(true); loadData(); }}
          className="flex items-center space-x-2 px-4 py-2 border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-xs font-bold transition-all"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh stats</span>
        </button>
      </div>

      {/* Grid of administrative summary statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Staff Accounts count */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Staff Accounts</span>
              <span className="text-3xl font-black text-slate-800 dark:text-white mt-1 block">{stats.total_users}</span>
              <span className="text-[10px] font-semibold text-primary mt-2 block">
                {stats.role_counts.Admin} Admins, {stats.role_counts.Physiotherapist} Therapists, {stats.role_counts.Doctor} Doctors
              </span>
            </div>
            <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
              <Users className="w-6 h-6 stroke-[2]" />
            </div>
          </div>

          {/* Patient records */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Patient Records</span>
              <span className="text-3xl font-black text-slate-800 dark:text-white mt-1 block">{stats.total_patients}</span>
              <span className="text-[10px] font-semibold text-teal-500 mt-2 block">Total profiles registered</span>
            </div>
            <div className="w-12 h-12 bg-teal-500/10 rounded-xl flex items-center justify-center text-teal-500">
              <UserCheck className="w-6 h-6 stroke-[2]" />
            </div>
          </div>

          {/* Assessments processed */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Assessments Run</span>
              <span className="text-3xl font-black text-slate-800 dark:text-white mt-1 block">{stats.total_assessments}</span>
              <span className="text-[10px] font-semibold text-indigo-500 mt-2 block">MediaPipe CV pose records</span>
            </div>
            <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center text-indigo-500">
              <Cpu className="w-6 h-6 stroke-[2]" />
            </div>
          </div>

        </div>
      )}

      {/* User Management and Audit Logs layout split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* User management list */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm lg:col-span-2 space-y-5 overflow-hidden">
          <div>
            <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Clinician Staff Accounts</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Manage user roles and clinical permissions.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 dark:text-slate-500 uppercase tracking-widest font-extrabold">
                  <th className="pb-3 pl-2">Name / Username</th>
                  <th className="pb-3">Email Address</th>
                  <th className="pb-3 text-center">Current Role</th>
                  <th className="pb-3 text-right pr-2">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {users.map((u) => (
                  <tr key={u._id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 pl-2">
                      <span className="font-bold text-slate-800 dark:text-slate-100 block">{u.full_name}</span>
                      <span className="text-[10px] text-slate-400 block font-semibold">@{u.username}</span>
                    </td>
                    <td className="py-3.5 text-slate-500 dark:text-slate-400 font-medium">
                      {u.email}
                    </td>
                    <td className="py-3.5 text-center">
                      <select
                        value={u.role}
                        onChange={(e) => handleUpdateRole(u._id, e.target.value)}
                        disabled={actionLoading === u._id}
                        className="px-2.5 py-1 bg-slate-50 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 rounded-lg font-bold text-[10px] text-slate-700 dark:text-slate-300 focus:outline-none focus:border-primary cursor-pointer disabled:opacity-50"
                      >
                        <option value="Admin">Admin</option>
                        <option value="Physiotherapist">Physiotherapist</option>
                        <option value="Doctor">Doctor</option>
                        <option value="Patient">Patient</option>
                      </select>
                    </td>
                    <td className="py-3.5 text-right pr-2">
                      <button
                        onClick={() => handleDeleteUser(u._id, u.username)}
                        disabled={actionLoading === u._id}
                        className="p-2 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/20 transition-all disabled:opacity-50"
                      >
                        <Trash2 className="w-4.5 h-4.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Audit Logs list */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between overflow-hidden">
          <div>
            <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Security Audit Logs</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Live tracking of clinical events.</p>
          </div>

          <div className="space-y-4 my-5 flex-grow overflow-y-auto max-h-[340px] pr-1 pt-1">
            {stats?.recent_logs.map((log, index) => (
              <div 
                key={index} 
                className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-100 dark:border-slate-800/60 text-[10px] space-y-1.5"
              >
                <div className="flex items-center justify-between font-semibold">
                  <span className={`px-1.5 py-0.5 rounded text-[8px] font-black ${
                    log.level === 'WARNING' ? 'bg-amber-500/10 text-amber-500' : 'bg-blue-500/10 text-blue-500'
                  }`}>
                    {log.level}
                  </span>
                  
                  <span className="text-slate-400 flex items-center space-x-1 font-medium">
                    <Clock className="w-3 h-3 mr-0.5" />
                    <span>{log.timestamp.slice(11, 19)}</span>
                  </span>
                </div>
                
                <p className="text-slate-700 dark:text-slate-300 font-bold leading-snug">
                  {log.action} <span className="font-medium text-slate-400">by @{log.user}</span>
                </p>
                <p className="text-slate-500 dark:text-slate-400 font-medium">
                  {log.details}
                </p>
              </div>
            ))}
          </div>

          <div className="border-t border-slate-100 dark:border-slate-800 pt-4 text-[10px] text-slate-400 font-semibold uppercase tracking-widest flex items-center space-x-1.5">
            <KeyRound className="w-4 h-4 text-primary" />
            <span>Audit trail compliant with clinical data privacy.</span>
          </div>
        </div>

      </div>

    </div>
  );
};
export default Admin;
