import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  Video, 
  TrendingUp, 
  Clock, 
  FileSpreadsheet, 
  PlusCircle, 
  UserCheck, 
  Activity, 
  ArrowRight,
  ClipboardList
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie
} from 'recharts';
import { motion } from 'framer-motion';
import { api, Patient, Assessment } from '../api';

export const Dashboard: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [patientsData, assessmentsData] = await Promise.all([
          api.patients.list(),
          api.assessments.list()
        ]);
        setPatients(patientsData);
        setAssessments(assessmentsData);
      } catch (err) {
        console.error('Error fetching dashboard statistics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Compute stats
  const totalPatients = patients.length;
  const totalAssessments = assessments.length;
  
  const improvingCount = patients.filter(p => p.current_status === 'Improving').length;
  const improvingRate = totalPatients > 0 ? Math.round((improvingCount / totalPatients) * 100) : 0;
  
  // Pending reviews: assessments with no doctor notes or session logged recently
  const pendingReviews = assessments.filter(a => !a.therapist_notes || a.therapist_notes.trim() === '').length;

  // Group assessments by impairment level for chart
  const impairmentCounts = assessments.reduce((acc, curr) => {
    const level = curr.predictions?.impairment_level || 'Normal';
    acc[level] = (acc[level] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieChartData = Object.entries(impairmentCounts).map(([name, value]) => ({
    name,
    value
  }));

  const COLORS = {
    'Normal': '#10B981', // green
    'Mild': '#3B82F6',   // blue
    'Moderate': '#F59E0B', // amber
    'Severe': '#EF4444',   // red
    'Very Severe': '#7F1D1D' // deep red
  };

  // Timeline series for AreaChart (daily assessments volume)
  const timelineData = assessments.reduce((acc, curr) => {
    const dateStr = curr.assessment_date.slice(0, 10);
    const existing = acc.find(item => item.date === dateStr);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ date: dateStr, count: 1 });
    }
    return acc;
  }, [] as { date: string; count: number }[]).sort((a, b) => a.date.localeCompare(b.date));

  // Quick activities list
  const recentActivities = assessments
    .slice()
    .reverse()
    .slice(0, 5)
    .map(a => {
      const patientName = patients.find(p => p.patient_id === a.patient_id || p._id === a.patient_id)?.name || 'Unknown Patient';
      return {
        id: a._id,
        patientName,
        sessionNumber: a.session_number,
        level: a.predictions?.impairment_level || 'Normal',
        date: new Date(a.assessment_date).toLocaleDateString(),
        speed: a.extracted_features?.gait?.walking_speed_ms || 0.0
      };
    });

  const cardsContainer = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
      }
    }
  };

  const cardItem = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring' as any, stiffness: 100 } }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded-xl w-48 mb-8"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          <div className="h-96 bg-slate-200 dark:bg-slate-800 rounded-2xl lg:col-span-2"></div>
          <div className="h-96 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 font-sans">
      {/* Welcome Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-800 dark:text-white">
            Clinical Dashboard
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1.5">
            Real-time gait & upper limb rehabilitation analytics.
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => navigate('/patients')}
            className="flex items-center space-x-2 px-5 py-2.5 bg-primary text-white text-xs font-bold rounded-xl shadow-md hover:bg-primary/95 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Manage Patients</span>
          </button>
        </div>
      </div>

      {/* Stats Counter Cards Grid */}
      <motion.div 
        variants={cardsContainer}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {/* Total Patients */}
        <motion.div variants={cardItem} className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Total Patients</span>
            <span className="text-3xl font-black text-slate-800 dark:text-white mt-1 block">{totalPatients}</span>
            <span className="text-[10px] font-semibold text-primary mt-2 block">Active medical records</span>
          </div>
          <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
            <Users className="w-6 h-6 stroke-[2.2]" />
          </div>
        </motion.div>

        {/* Today's Assessments */}
        <motion.div variants={cardItem} className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Total Assessments</span>
            <span className="text-3xl font-black text-slate-800 dark:text-white mt-1 block">{totalAssessments}</span>
            <span className="text-[10px] font-semibold text-teal-500 mt-2 block">MediaPipe Pose reports</span>
          </div>
          <div className="w-12 h-12 bg-teal-500/10 rounded-xl flex items-center justify-center text-teal-500">
            <Video className="w-6 h-6 stroke-[2.2]" />
          </div>
        </motion.div>

        {/* Recovery Rate */}
        <motion.div variants={cardItem} className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Patients Improving</span>
            <span className="text-3xl font-black text-slate-800 dark:text-white mt-1 block">{improvingRate}%</span>
            <span className="text-[10px] font-semibold text-teal-500 mt-2 block">{improvingCount} patients recovering</span>
          </div>
          <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-500">
            <TrendingUp className="w-6 h-6 stroke-[2.2]" />
          </div>
        </motion.div>

        {/* Pending Reviews */}
        <motion.div variants={cardItem} className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">Unsigned Notes</span>
            <span className="text-3xl font-black text-slate-800 dark:text-white mt-1 block">{pendingReviews}</span>
            <span className="text-[10px] font-semibold text-amber-500 mt-2 block">Require clinical details</span>
          </div>
          <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center text-amber-500">
            <Clock className="w-6 h-6 stroke-[2.2]" />
          </div>
        </motion.div>
      </motion.div>

      {/* Main Charts & Visual Overview section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Gait Sessions Timeline Chart (Area) */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Rehab Assessment Logs</h3>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Diagnostic volumes over time</p>
            </div>
          </div>
          
          <div className="h-80 w-full">
            {timelineData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timelineData}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" className="dark:hidden" />
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" className="hidden dark:block" />
                  <XAxis dataKey="date" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ 
                      borderRadius: '12px', 
                      background: '#1E293B', 
                      color: '#FFF', 
                      borderColor: '#475569' 
                    }} 
                  />
                  <Area type="monotone" dataKey="count" name="Diagnostics Run" stroke="#2563EB" strokeWidth={2.5} fillOpacity={1} fill="url(#colorCount)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 dark:text-slate-600 text-xs">
                No timeseries logs available.
              </div>
            )}
          </div>
        </div>

        {/* AI Prediction Distribution (PieChart) */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Impairment Severity Range</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Severity distribution of all runs</p>
          </div>

          <div className="h-56 w-full flex justify-center items-center relative">
            {pieChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieChartData.map((entry, index) => {
                      const col = COLORS[entry.name as keyof typeof COLORS] || '#94A3B8';
                      return <Cell key={`cell-${index}`} fill={col} />;
                    })}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-400 text-xs">No distribution data</div>
            )}
            
            {/* Center HUD count */}
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-2xl font-black text-slate-800 dark:text-white">{totalAssessments}</span>
              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Runs</span>
            </div>
          </div>

          {/* Color Indicators Legend */}
          <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800 text-[10px]">
            {Object.entries(COLORS).map(([name, color]) => {
              const count = impairmentCounts[name] || 0;
              return (
                <div key={name} className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                  <div className="flex items-center space-x-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }}></div>
                    <span className="font-semibold">{name}</span>
                  </div>
                  <span className="font-bold text-slate-800 dark:text-white">{count} ({totalAssessments > 0 ? Math.round(count/totalAssessments*100) : 0}%)</span>
                </div>
              );
            })}
          </div>
        </div>

      </div>

      {/* Row 3: Recent Assessments Table & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Latest Assessments Table */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm lg:col-span-2 overflow-hidden">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Latest Pose Diagnoses</h3>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Recently compiled motor reports</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            {recentActivities.length > 0 ? (
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 dark:text-slate-500 uppercase tracking-widest font-extrabold">
                    <th className="pb-3 pl-2">Patient</th>
                    <th className="pb-3">Session</th>
                    <th className="pb-3">Analysis Date</th>
                    <th className="pb-3 text-center">AI Rating</th>
                    <th className="pb-3 text-right pr-2">Gait Speed</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {recentActivities.map((act) => {
                    const statusColor = COLORS[act.level as keyof typeof COLORS] || '#94A3B8';
                    return (
                      <tr 
                        key={act.id} 
                        onClick={() => navigate(`/patients/${act.patientName}`)}
                        className="group hover:bg-slate-50 dark:hover:bg-slate-800/40 cursor-pointer transition-colors"
                      >
                        <td className="py-3.5 pl-2 font-bold text-slate-800 dark:text-slate-100 group-hover:text-primary">
                          {act.patientName}
                        </td>
                        <td className="py-3.5 font-semibold text-slate-500 dark:text-slate-400">
                          S{act.sessionNumber}
                        </td>
                        <td className="py-3.5 text-slate-400 dark:text-slate-500">
                          {act.date}
                        </td>
                        <td className="py-3.5 text-center">
                          <span 
                            className="inline-block px-2.5 py-0.5 rounded-full font-bold text-[10px]"
                            style={{ backgroundColor: `${statusColor}15`, color: statusColor }}
                          >
                            {act.level}
                          </span>
                        </td>
                        <td className="py-3.5 text-right font-bold text-slate-700 dark:text-slate-300 pr-2">
                          {act.speed} m/s
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <div className="text-center py-8 text-slate-400 text-xs">
                No assessments logged yet. Open Patients to add a new assessment.
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions Portal */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Quick Clinical Actions</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Diagnostic tools and shortcuts</p>
          </div>
          
          <div className="space-y-3.5 my-6 flex-grow flex flex-col justify-center">
            <button 
              onClick={() => navigate('/patients')}
              className="flex items-center justify-between p-3.5 bg-slate-50 hover:bg-primary/5 dark:bg-slate-800/40 dark:hover:bg-slate-800 rounded-xl group transition-all"
            >
              <div className="flex items-center space-x-3 text-slate-700 dark:text-slate-300">
                <PlusCircle className="w-5 h-5 text-primary" />
                <span className="font-bold text-xs">Register Patient Profile</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <button 
              onClick={() => navigate('/patients')}
              className="flex items-center justify-between p-3.5 bg-slate-50 hover:bg-teal-500/5 dark:bg-slate-800/40 dark:hover:bg-slate-800 rounded-xl group transition-all"
            >
              <div className="flex items-center space-x-3 text-slate-700 dark:text-slate-300">
                <Video className="w-5 h-5 text-teal-500" />
                <span className="font-bold text-xs">Run MediaPipe Gait Analysis</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <button 
              onClick={() => navigate('/patients')}
              className="flex items-center justify-between p-3.5 bg-slate-50 hover:bg-amber-500/5 dark:bg-slate-800/40 dark:hover:bg-slate-800 rounded-xl group transition-all"
            >
              <div className="flex items-center space-x-3 text-slate-700 dark:text-slate-300">
                <ClipboardList className="w-5 h-5 text-amber-500" />
                <span className="font-bold text-xs">Log Clinical Metrics (FMA/BBS)</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          <div className="bg-blue-500/5 border border-blue-500/10 p-3.5 rounded-xl text-[10px] text-blue-600 dark:text-blue-400 font-semibold flex items-start space-x-2">
            <Activity className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>
              All body pose processing conforms to MediaPipe 33-Keypoint skeleton models.
            </span>
          </div>
        </div>

      </div>

    </div>
  );
};
export default Dashboard;
