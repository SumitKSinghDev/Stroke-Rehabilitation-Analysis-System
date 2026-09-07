import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, ShieldAlert, Lock, User, Eye, EyeOff, Loader2 } from 'lucide-react';
import { api } from '../api';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please fill in all credentials.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.auth.login(username, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Quick Login utility for presentation sessions
  const handleQuickLogin = async (role: 'admin' | 'therapist' | 'doctor') => {
    setLoading(true);
    setError('');
    const credentials = {
      admin: { u: 'admin', p: 'admin123' },
      therapist: { u: 'therapist', p: 'therapist123' },
      doctor: { u: 'doctor', p: 'doctor123' }
    };
    const { u, p } = credentials[role];
    try {
      await api.auth.login(u, p);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Quick login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center items-center px-4 relative overflow-hidden font-sans">
      {/* Background visual neon orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-md bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 p-8 rounded-3xl shadow-2xl z-10">
        
        {/* Brand Banner */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 bg-primary/15 rounded-2xl flex items-center justify-center text-primary mb-4 border border-primary/20">
            <Activity className="w-8 h-8 stroke-[2.5] animate-pulse" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-wider">RehabShield</h1>
          <p className="text-xs text-slate-400 font-semibold tracking-wider uppercase mt-1">Stroke Rehabilitation Decision Support</p>
        </div>

        {error && (
          <div className="mb-5 p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400 text-xs font-semibold flex items-center space-x-2.5">
            <ShieldAlert className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          
          {/* Username Input */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-1">
              Username
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-500">
                <User className="w-5 h-5" />
              </span>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter clinician username"
                className="w-full pl-11 pr-4 py-3 bg-slate-950/40 border border-slate-700 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-primary text-sm transition-all focus:ring-1 focus:ring-primary/30"
                disabled={loading}
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-1">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-500">
                <Lock className="w-5 h-5" />
              </span>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="w-full pl-11 pr-11 py-3 bg-slate-950/40 border border-slate-700 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-primary text-sm transition-all focus:ring-1 focus:ring-primary/30"
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-500 hover:text-slate-300"
                disabled={loading}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full py-3 bg-primary hover:bg-primary/90 text-white font-bold rounded-2xl shadow-lg shadow-primary/20 flex items-center justify-center space-x-2 text-sm transition-all active:scale-[0.99] disabled:opacity-50"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>

        {/* Quick Login Shortcuts */}
        <div className="mt-8 pt-6 border-t border-slate-700/50">
          <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase text-center mb-3">
            Quick Clinical Access Shortcuts
          </p>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => handleQuickLogin('admin')}
              className="py-2 bg-slate-950/30 hover:bg-slate-950/60 border border-slate-700/50 hover:border-slate-600 rounded-xl text-[10px] font-extrabold text-slate-300 transition-all active:scale-95"
              disabled={loading}
            >
              Admin Portal
            </button>
            <button
              onClick={() => handleQuickLogin('therapist')}
              className="py-2 bg-slate-950/30 hover:bg-slate-950/60 border border-slate-700/50 hover:border-slate-600 rounded-xl text-[10px] font-extrabold text-slate-300 transition-all active:scale-95"
              disabled={loading}
            >
              Therapist
            </button>
            <button
              onClick={() => handleQuickLogin('doctor')}
              className="py-2 bg-slate-950/30 hover:bg-slate-950/60 border border-slate-700/50 hover:border-slate-600 rounded-xl text-[10px] font-extrabold text-slate-300 transition-all active:scale-95"
              disabled={loading}
            >
              Doctor MD
            </button>
          </div>
        </div>

      </div>
      
      {/* Footer system status */}
      <div className="mt-6 text-[10px] text-slate-500 font-semibold uppercase tracking-widest z-10">
        RehabShield Client v1.0.0 (FastAPI-Connected)
      </div>
    </div>
  );
};
export default Login;
