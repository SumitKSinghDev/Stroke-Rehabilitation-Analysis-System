import React, { useState } from 'react';
import { 
  User, 
  Lock, 
  Sun, 
  Moon, 
  Settings as SettingsIcon, 
  CheckCircle2, 
  Loader2, 
  AlertCircle 
} from 'lucide-react';
import { api, getStoredUser, setStoredUser } from '../api';

interface SettingsProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ darkMode, toggleDarkMode }) => {
  const user = getStoredUser();

  // Profile Form States
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [profileError, setProfileError] = useState('');

  // Password Form States
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  // System Configurations (Mock States saved in localStorage)
  const [useMockDB, setUseMockDB] = useState(() => {
    return localStorage.getItem('rehab_mock_db') !== 'false';
  });
  const [useCVSimulator, setUseCVSimulator] = useState(() => {
    return localStorage.getItem('rehab_cv_sim') !== 'false';
  });

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email) {
      setProfileError('Please fill in all profile fields.');
      return;
    }

    setProfileLoading(true);
    setProfileError('');
    setProfileSuccess(false);

    try {
      const updatedUser = await api.auth.updateProfile({ full_name: fullName, email });
      setStoredUser(updatedUser);
      setProfileSuccess(true);
    } catch (err: any) {
      setProfileError(err.message || 'Failed to update profile.');
    } finally {
      setProfileLoading(false);
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!oldPassword || !newPassword || !confirmPassword) {
      setPasswordError('Please fill in all password fields.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    setPasswordLoading(true);
    setPasswordError('');
    setPasswordSuccess(false);

    try {
      await api.auth.updatePassword({ old_password: oldPassword, new_password: newPassword });
      setPasswordSuccess(true);
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPasswordError(err.message || 'Password update failed.');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleToggleMockDB = (val: boolean) => {
    setUseMockDB(val);
    localStorage.setItem('rehab_mock_db', val ? 'true' : 'false');
  };

  const handleToggleCVSimulator = (val: boolean) => {
    setUseCVSimulator(val);
    localStorage.setItem('rehab_cv_sim', val ? 'true' : 'false');
  };

  return (
    <div className="space-y-8 font-sans max-w-4xl">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight">System Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Clinician profile, passwords, visual theme, and algorithmic testing fallbacks.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Profile Settings card */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-5">
          <div className="flex items-center space-x-2 text-slate-800 dark:text-white">
            <User className="w-5 h-5 text-primary" />
            <h3 className="font-extrabold text-sm">Clinician Profile</h3>
          </div>

          <form onSubmit={handleUpdateProfile} className="space-y-4">
            {profileSuccess && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 rounded-xl text-xs font-bold flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>Profile updated successfully!</span>
              </div>
            )}
            
            {profileError && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-500 rounded-xl text-xs font-bold flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{profileError}</span>
              </div>
            )}

            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Clinician Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
              />
            </div>

            <button
              type="submit"
              disabled={profileLoading}
              className="px-4 py-2.5 bg-primary text-white text-xs font-bold rounded-xl shadow-md hover:bg-primary/95 flex items-center space-x-1.5 active:scale-95 disabled:opacity-50"
            >
              {profileLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <span>Save Profile</span>
              )}
            </button>
          </form>
        </div>

        {/* Change Password card */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-5">
          <div className="flex items-center space-x-2 text-slate-800 dark:text-white">
            <Lock className="w-5 h-5 text-primary" />
            <h3 className="font-extrabold text-sm">Security & Password</h3>
          </div>

          <form onSubmit={handleUpdatePassword} className="space-y-4">
            {passwordSuccess && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 rounded-xl text-xs font-bold flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>Password changed successfully!</span>
              </div>
            )}
            
            {passwordError && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-500 rounded-xl text-xs font-bold flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{passwordError}</span>
              </div>
            )}

            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Old Password</label>
              <input
                type="password"
                required
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs focus:outline-none focus:border-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">New Password</label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Confirm New</label>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={passwordLoading}
              className="px-4 py-2.5 bg-primary text-white text-xs font-bold rounded-xl shadow-md hover:bg-primary/95 flex items-center space-x-1.5 active:scale-95 disabled:opacity-50"
            >
              {passwordLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Changing...</span>
                </>
              ) : (
                <span>Update Password</span>
              )}
            </button>
          </form>
        </div>

        {/* Theme Settings card */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-slate-800 dark:text-white">
            <Sun className="w-5 h-5 text-primary" />
            <h3 className="font-extrabold text-sm">Visual Theme</h3>
          </div>
          
          <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Toggle dashboard interface styles.</p>

          <div className="grid grid-cols-2 gap-4 pt-2">
            <button
              onClick={() => { if (darkMode) toggleDarkMode(); }}
              className={`p-4 rounded-2xl border flex flex-col items-center justify-center space-y-2 cursor-pointer transition-all ${
                !darkMode 
                  ? 'bg-primary/5 border-primary text-primary font-bold shadow-sm' 
                  : 'bg-slate-50 dark:bg-slate-850 border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Sun className="w-6 h-6" />
              <span className="text-xs font-bold">Light Medical</span>
            </button>

            <button
              onClick={() => { if (!darkMode) toggleDarkMode(); }}
              className={`p-4 rounded-2xl border flex flex-col items-center justify-center space-y-2 cursor-pointer transition-all ${
                darkMode 
                  ? 'bg-primary/10 border-primary text-primary font-bold shadow-sm' 
                  : 'bg-slate-50 dark:bg-slate-850 border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Moon className="w-6 h-6" />
              <span className="text-xs font-bold">Dark Cyber-Rehab</span>
            </button>
          </div>
        </div>

        {/* Testing Fallbacks Configuration card */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-slate-800 dark:text-white">
            <SettingsIcon className="w-5 h-5 text-primary" />
            <h3 className="font-extrabold text-sm">Testing & Simulation Config</h3>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Configure algorithm execution parameters for evaluation.</p>

          <div className="space-y-4 pt-2 text-xs">
            {/* Mock DB */}
            <div className="flex items-center justify-between">
              <div>
                <span className="font-bold text-slate-700 dark:text-slate-300 block">Mock Local JSON Database</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Use JSON files if MongoDB is down.</span>
              </div>
              <input
                type="checkbox"
                checked={useMockDB}
                onChange={(e) => handleToggleMockDB(e.target.checked)}
                className="w-4 h-4 text-primary focus:ring-primary/20 rounded cursor-pointer"
              />
            </div>

            {/* CV Sim */}
            <div className="flex items-center justify-between">
              <div>
                <span className="font-bold text-slate-700 dark:text-slate-300 block">Video Gait CV Simulator</span>
                <span className="text-[10px] text-slate-400 block mt-0.5">Simulate MediaPipe outputs for quick tests.</span>
              </div>
              <input
                type="checkbox"
                checked={useCVSimulator}
                onChange={(e) => handleToggleCVSimulator(e.target.checked)}
                className="w-4 h-4 text-primary focus:ring-primary/20 rounded cursor-pointer"
              />
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
export default Settings;
