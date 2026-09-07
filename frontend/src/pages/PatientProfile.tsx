import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  User, 
  Activity, 
  Video, 
  TrendingUp, 
  FileText, 
  Plus, 
  ArrowLeft,
  ChevronRight,
  ClipboardList,
  AlertCircle,
  Sparkles,
  Download,
  Calendar,
  CheckCircle,
  Cpu,
  Loader2,
  Trash2,
  Dumbbell,
  Target,
  Zap,
  Clock,
  ShieldCheck
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { api, Patient, Assessment, ProgressSummary } from '../api';
import SkeletonViewer from '../components/SkeletonViewer';

export const PatientProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [patient, setPatient] = useState<Patient | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [progress, setProgress] = useState<ProgressSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'sessions' | 'trends' | 'new_run' | 'inspector'>('sessions');

  // Inspection state for detailed view of a session
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);

  // New assessment form states
  const [sessionNumber, setSessionNumber] = useState(1);
  const [fmaScore, setFmaScore] = useState('');
  const [bbsScore, setBbsScore] = useState('');
  const [facScore, setFacScore] = useState('');
  const [tugScore, setTugScore] = useState('');
  const [modelUsed, setModelUsed] = useState('Random Forest');
  const [therapistNotes, setTherapistNotes] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [formError, setFormError] = useState('');
  const [scanProgress, setScanProgress] = useState<number | null>(null);

  const handleCreateAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patient) return;

    if (!videoFile) {
      setFormError("Upload a walking video to begin analysis.");
      return;
    }

    setAnalyzing(true);
    setFormError('');
    setScanProgress(10);

    try {
      const formData = new FormData();
      formData.append('patient_id', patient.patient_id);
      formData.append('session_number', sessionNumber.toString());
      formData.append('fma_score', fmaScore);
      formData.append('bbs_score', bbsScore);
      formData.append('fac_score', facScore);
      formData.append('tug_score', tugScore);
      formData.append('model_used', modelUsed);
      formData.append('therapist_notes', therapistNotes);
      formData.append('video', videoFile);

      setScanProgress(50);
      const newSess = await api.assessments.create(formData);
      setScanProgress(100);

      await loadData();
      setVideoFile(null);
      setTherapistNotes('');
      setSelectedAssessment(newSess);
      setActiveTab('inspector');
    } catch (err: any) {
      console.error("Assessment creation error:", err);
      setFormError(err.message || "No valid pose detected in the uploaded video.");
    } finally {
      setAnalyzing(false);
      setScanProgress(null);
    }
  };

  const handleDeletePatient = async () => {
    if (!patient) return;
    if (window.confirm(`Are you sure you want to permanently delete Patient ${patient.name}? This will delete all session histories.`)) {
      try {
        await api.patients.delete(patient.patient_id);
        navigate('/patients');
      } catch (err) {
        alert('Failed to delete patient profile.');
      }
    }
  };

  const handleDownloadReport = async (assessmentId: string, sessionNum: number) => {
    try {
      const filename = `rehab_report_session_${sessionNum}.pdf`;
      await api.reports.download(assessmentId, filename);
    } catch (err) {
      alert("Failed to download PDF report. Please verify connection.");
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
        <div className="h-28 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>
        <div className="h-96 bg-slate-200 dark:bg-slate-800 rounded-3xl mt-8"></div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-6 rounded-2xl flex items-center space-x-3">
        <AlertCircle className="w-5 h-5" />
        <span>Patient record not found.</span>
      </div>
    );
  }

  // Define tab headers
  const tabs = [
    { id: 'sessions', label: 'Diagnostics Log', icon: FileText },
    { id: 'trends', label: 'Recovery Trends', icon: TrendingUp },
    { id: 'new_run', label: 'New Movement Analysis', icon: Plus },
  ];

  if (assessments.length > 0) {
    tabs.push({ id: 'inspector', label: 'Biomechanical Inspector', icon: Cpu });
  }

  const getSeverityBadgeColor = (level: string) => {
    switch (level) {
      case 'Normal': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/25';
      case 'Mild': return 'bg-blue-500/10 text-blue-500 border-blue-500/25';
      case 'Moderate': return 'bg-amber-500/10 text-amber-500 border-amber-500/25';
      case 'Severe': return 'bg-rose-500/10 text-rose-500 border-rose-500/25';
      case 'Very Severe': return 'bg-red-900/20 text-red-400 border-red-900/30';
      default: return 'bg-slate-500/10 text-slate-500 border-slate-500/25';
    }
  };

  return (
    <div className="space-y-8 font-sans">
      
      {/* Back button */}
      <button 
        onClick={() => navigate('/patients')}
        className="flex items-center space-x-2 text-xs font-bold text-slate-500 hover:text-primary transition-colors cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Directory</span>
      </button>

      {/* Patient HUD Demographics Banner */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="flex items-start space-x-4">
          <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center text-primary border border-primary/20">
            <User className="w-8 h-8 stroke-[1.8]" />
          </div>
          <div>
            <div className="flex items-center space-x-3 flex-wrap">
              <h2 className="text-2xl font-extrabold text-slate-800 dark:text-white leading-snug">{patient.name}</h2>
              <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded-md">
                {patient.patient_id}
              </span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-x-6 gap-y-1.5 mt-3 text-xs text-slate-500 dark:text-slate-400 font-semibold">
              <div>Age/Sex: <span className="text-slate-800 dark:text-slate-200">{patient.age} yrs / {patient.gender}</span></div>
              <div>Stroke Classification: <span className="text-slate-800 dark:text-slate-200">{patient.stroke_type}</span></div>
              <div>Observed Asymmetry Side: <span className="text-red-500">{patient.affected_side}</span></div>
              <div>Onset Date: <span className="text-slate-800 dark:text-slate-200">{patient.stroke_date}</span></div>
            </div>
          </div>
        </div>

        {/* Status indicator and delete actions */}
        <div className="flex lg:flex-col items-start lg:items-end justify-between border-t lg:border-t-0 pt-4 lg:pt-0 border-slate-100 dark:border-slate-800">
          <div className="text-right">
            <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider mb-1">Clinical Status</span>
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold border ${
              patient.current_status === 'Improving' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
              patient.current_status === 'Stable' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
              'bg-rose-500/10 text-rose-500 border-rose-500/20'
            }`}>
              {patient.current_status}
            </span>
          </div>
          <button
            onClick={handleDeletePatient}
            className="flex items-center space-x-1 text-red-500 hover:text-red-700 text-[10px] font-bold uppercase tracking-wider mt-3"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Archive Profile</span>
          </button>
        </div>
      </div>

      {/* Tabs navigation panel */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 space-x-6 text-sm font-semibold">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as any);
                setFormError('');
              }}
              className={`pb-4 px-1 flex items-center space-x-2 transition-colors relative cursor-pointer ${
                activeTab === tab.id 
                  ? 'text-primary' 
                  : 'text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full"></div>
              )}
            </button>
          );
        })}
      </div>

      {/* Tabs contents */}
      
      {/* 1. SESSIONS TABLE TAB */}
      {activeTab === 'sessions' && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Diagnostics Session Records</h3>
            {progress?.improvement_pct !== undefined && progress.session_count > 1 && (
              <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-xs font-bold rounded-xl flex items-center space-x-2">
                <Sparkles className="w-4 h-4" />
                <span>Overall Motor Improvement: +{progress.improvement_pct}%</span>
              </div>
            )}
          </div>

          <div className="overflow-x-auto">
            {assessments.length > 0 ? (
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 dark:text-slate-500 uppercase tracking-widest font-extrabold">
                    <th className="pb-3 pl-2">Session</th>
                    <th className="pb-3">Date</th>
                    <th className="pb-3 text-center">Model Classification</th>
                    <th className="pb-3 text-center">FMA Score</th>
                    <th className="pb-3 text-center">BBS Score</th>
                    <th className="pb-3 text-center">TUG Time</th>
                    <th className="pb-3 text-right pr-2">Report & Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {assessments.map((s) => (
                    <tr 
                      key={s._id} 
                      className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <td className="py-3.5 pl-2 font-black text-slate-800 dark:text-slate-100">
                        Session #{s.session_number}
                      </td>
                      <td className="py-3.5 text-slate-400 dark:text-slate-500">
                        {new Date(s.assessment_date).toLocaleDateString()}
                      </td>
                      <td className="py-3.5 text-center">
                        <span className={`inline-block px-2.5 py-0.5 rounded-full font-bold text-[10px] border ${getSeverityBadgeColor(s.predictions?.impairment_level)}`}>
                          {s.predictions?.impairment_level}
                        </span>
                      </td>
                      <td className="py-3.5 text-center font-semibold text-slate-700 dark:text-slate-300">
                        {s.clinical_scores.fma_score} <span className="text-[10px] text-slate-400">/226</span>
                      </td>
                      <td className="py-3.5 text-center font-semibold text-slate-700 dark:text-slate-300">
                        {s.clinical_scores.bbs_score} <span className="text-[10px] text-slate-400">/56</span>
                      </td>
                      <td className="py-3.5 text-center font-semibold text-slate-700 dark:text-slate-300">
                        {s.clinical_scores.tug_score}s
                      </td>
                      <td className="py-3.5 text-right pr-2 space-x-2">
                        <button
                          onClick={() => {
                            setSelectedAssessment(s);
                            setActiveTab('inspector');
                          }}
                          className="px-2.5 py-1.5 bg-slate-100 hover:bg-primary/10 hover:text-primary dark:bg-slate-800 dark:hover:bg-slate-700 rounded-lg font-bold text-[10px] transition-colors"
                        >
                          Inspector
                        </button>
                        <button
                          onClick={() => handleDownloadReport(s._id, s.session_number)}
                          className="px-2.5 py-1.5 bg-primary/10 text-primary hover:bg-primary hover:text-white rounded-lg font-bold text-[10px] transition-all flex inline-flex items-center space-x-1"
                        >
                          <Download className="w-3 h-3" />
                          <span>PDF</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="text-center py-12 text-slate-400">
                <ClipboardList className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="font-semibold text-sm">No session assessments logged for this patient yet.</p>
                <button
                  onClick={() => setActiveTab('new_run')}
                  className="mt-4 px-4 py-2 bg-primary text-white rounded-xl text-xs font-bold hover:bg-primary/95"
                >
                  Create Session Baseline
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 2. RECOVERY TRENDS TAB */}
      {activeTab === 'trends' && (
        <div className="space-y-6">
          
          {/* Trends Summary Panel */}
          {progress && progress.session_count > 1 ? (
            <>
              {/* Quick improvements overview cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
                  <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Walking Speed Gain</span>
                  <div className="flex items-baseline space-x-2 mt-2">
                    <span className="text-2xl font-black text-slate-800 dark:text-white">
                      +{progress.recent_comparison.walking_speed?.improvement_pct}%
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      ({progress.recent_comparison.walking_speed?.initial} → {progress.recent_comparison.walking_speed?.current} m/s)
                    </span>
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
                  <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Balance Sway Control</span>
                  <div className="flex items-baseline space-x-2 mt-2">
                    <span className="text-2xl font-black text-slate-800 dark:text-white">
                      +{progress.recent_comparison.balance?.improvement_pct}%
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      ({progress.recent_comparison.balance?.initial} → {progress.recent_comparison.balance?.current} pts)
                    </span>
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
                  <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Knee Flexion Range</span>
                  <div className="flex items-baseline space-x-2 mt-2">
                    <span className="text-2xl font-black text-slate-800 dark:text-white">
                      +{progress.recent_comparison.knee_angle?.improvement_pct}%
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      ({progress.recent_comparison.knee_angle?.initial}° → {progress.recent_comparison.knee_angle?.current}°)
                    </span>
                  </div>
                </div>
              </div>

              {/* Progress Graphs */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Gait parameters line */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm">
                  <h3 className="font-extrabold text-slate-800 dark:text-white text-sm mb-4">Gait Speed & Balance Stability</h3>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={progress.recovery_timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" className="dark:hidden" />
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" className="hidden dark:block" />
                        <XAxis dataKey="session_number" tickFormatter={(v) => `S${v}`} stroke="#94A3B8" fontSize={10} />
                        <YAxis stroke="#94A3B8" fontSize={10} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '10px' }} />
                        <Line type="monotone" dataKey="walking_speed" name="Speed Index" stroke="#2563EB" strokeWidth={2.5} activeDot={{ r: 6 }} />
                        <Line type="monotone" dataKey="balance" name="Balance Score (%)" stroke="#14B8A6" strokeWidth={2.5} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Range of motion line */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm">
                  <h3 className="font-extrabold text-slate-800 dark:text-white text-sm mb-4">Anatomical Joint Angles Range</h3>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={progress.recovery_timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" className="dark:hidden" />
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" className="hidden dark:block" />
                        <XAxis dataKey="session_number" tickFormatter={(v) => `S${v}`} stroke="#94A3B8" fontSize={10} />
                        <YAxis stroke="#94A3B8" fontSize={10} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '10px' }} />
                        <Line type="monotone" dataKey="knee_angle" name="Knee Extension (°)" stroke="#EF4444" strokeWidth={2.5} />
                        <Line type="monotone" dataKey="hip_angle" name="Hip Extension (°)" stroke="#F59E0B" strokeWidth={2.5} />
                        <Line type="monotone" dataKey="upper_limb_movement" name="Upper Limb Rom (%)" stroke="#06B6D4" strokeWidth={2.5} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>
            </>
          ) : (
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-12 text-center rounded-3xl">
              <TrendingUp className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <p className="font-semibold text-slate-500 text-sm">
                Progress tracking graphs require at least two logged clinical sessions.
              </p>
            </div>
          )}
        </div>
      )}

      {/* 3. NEW MOVEMENT ANALYSIS TAB (VIDEO UPLOAD & CV ANALYSIS RUN) */}
      {activeTab === 'new_run' && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-6">
          <div>
            <h3 className="font-extrabold text-slate-800 dark:text-white text-base">New Movement Analysis Session</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Upload patient movement videos and log clinical validation scales.</p>
          </div>

          <form onSubmit={handleCreateAssessment} className="space-y-6">
            {formError && (
              <div className="p-3.5 bg-rose-500/10 border border-rose-500/30 text-rose-500 rounded-xl text-xs font-bold flex items-center space-x-2.5">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Left Column: Form Scores */}
              <div className="space-y-4 md:col-span-2">
                <h4 className="font-extrabold text-xs text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-0.5">
                  Clinician-Entered Assessment Metrics (Optional)
                </h4>
                
                <div className="grid grid-cols-2 gap-4">
                  {/* FMA */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Fugl-Meyer Score (FMA)</label>
                    <input
                      type="number"
                      min="0"
                      max="226"
                      placeholder="Optional (0-226)"
                      value={fmaScore}
                      onChange={(e) => setFmaScore(e.target.value)}
                      className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                    />
                    <p className="text-[9px] text-slate-400 mt-1">Clinician score. Range: 0-226</p>
                  </div>

                  {/* BBS */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Berg Balance Scale (BBS)</label>
                    <input
                      type="number"
                      min="0"
                      max="56"
                      placeholder="Optional (0-56)"
                      value={bbsScore}
                      onChange={(e) => setBbsScore(e.target.value)}
                      className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                    />
                    <p className="text-[9px] text-slate-400 mt-1">Clinician score. Range: 0-56</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {/* FAC */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Functional Ambulation Categories (FAC)</label>
                    <select
                      value={facScore}
                      onChange={(e) => setFacScore(e.target.value)}
                      className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                    >
                      <option value="">Not assessed</option>
                      <option value="0">0: Non-functional walker</option>
                      <option value="1">1: Dependent level II assistant</option>
                      <option value="2">2: Dependent level I assistant</option>
                      <option value="3">3: Dependent supervision</option>
                      <option value="4">4: Independent on level ground</option>
                      <option value="5">5: Independent everywhere</option>
                    </select>
                  </div>

                  {/* TUG */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Timed Up & Go (TUG)</label>
                    <input
                      type="text"
                      placeholder="Optional (seconds)"
                      value={tugScore}
                      onChange={(e) => setTugScore(e.target.value)}
                      className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                    />
                    <p className="text-[9px] text-slate-400 mt-1">Seconds to stand, walk 3m, return & sit.</p>
                  </div>
                </div>

                {/* Session number & ML Model selector */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Session Order</label>
                    <input
                      type="number"
                      required
                      min="1"
                      value={sessionNumber}
                      onChange={(e) => setSessionNumber(parseInt(e.target.value) || 1)}
                      className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Classifier Model</label>
                    <select
                      value={modelUsed}
                      onChange={(e) => setModelUsed(e.target.value)}
                      className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary cursor-pointer"
                    >
                      <option value="Random Forest">Random Forest Classifier</option>
                      <option value="SVM">Support Vector Machine (SVM)</option>
                      <option value="XGBoost">XGBoost Classifier (Ensemble)</option>
                    </select>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 pl-0.5">Physiotherapist Notes</label>
                  <textarea
                    rows={3}
                    placeholder="Specific step discrepancies, arm swing observations..."
                    value={therapistNotes}
                    onChange={(e) => setTherapistNotes(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary resize-none"
                  />
                </div>

              </div>

              {/* Right Column: Video Upload */}
              <div className="space-y-4">
                <h4 className="font-extrabold text-xs text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-0.5">
                  Pose Assessment Video *
                </h4>
                
                <div className="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-6 text-center hover:border-primary hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-all flex flex-col justify-center items-center h-64 relative cursor-pointer">
                  <input
                    type="file"
                    accept="video/mp4,video/avi,video/mov"
                    onChange={handleVideoChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={analyzing}
                  />
                  {videoFile ? (
                    <div className="space-y-2">
                      <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary mx-auto">
                        <Video className="w-6 h-6" />
                      </div>
                      <span className="font-bold text-xs text-slate-700 dark:text-slate-300 block max-w-[200px] truncate">{videoFile.name}</span>
                      <span className="text-[10px] text-slate-400 block">{(videoFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                      <button
                        type="button"
                        onClick={() => {
                          setVideoFile(null);
                          setSelectedAssessment(null);
                          setFormError('');
                          setTherapistNotes('');
                          setFmaScore('');
                          setBbsScore('');
                          setFacScore('');
                          setTugScore('');
                        }}
                        className="text-red-500 font-semibold text-[10px] uppercase tracking-wider mt-1 hover:underline relative z-10"
                      >
                        Remove file
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center text-slate-400 mx-auto">
                        <Video className="w-6 h-6" />
                      </div>
                      <span className="font-bold text-xs text-slate-700 dark:text-slate-300 block">Upload gait clip</span>
                      <span className="text-[10px] text-slate-400 block">Supports MP4, AVI, MOV</span>
                    </div>
                  )}
                </div>

                <div className="p-3 bg-blue-500/5 rounded-xl text-[9px] text-blue-600 dark:text-blue-400 font-semibold">
                  Note: Upload a clear full-body video of the patient walking under good lighting for MediaPipe 33-landmark feature extraction and movement analysis.
                </div>
              </div>

            </div>

            {/* Form Footer action */}
            <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex justify-end">
              <button
                type="submit"
                disabled={analyzing}
                className="px-6 py-3 bg-primary text-white rounded-2xl font-bold shadow-lg shadow-primary/20 text-xs hover:bg-primary/95 flex items-center space-x-2 transition-all cursor-pointer active:scale-95 disabled:opacity-50"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>
                      {scanProgress !== null ? `Scanning Video Frames: ${scanProgress}%` : 'Processing MediaPipe Pose & ML Prediction...'}
                    </span>
                  </>
                ) : (
                  <>
                    <Cpu className="w-4 h-4" />
                    <span>Run Diagnostic Analysis</span>
                  </>
                )}
              </button>
            </div>
          </form>

        </div>
      )}

      {/* 4. SKELETON INSPECTOR TAB (BIOMECHANICAL ANALYSIS DISPLAY) */}
      {activeTab === 'inspector' && selectedAssessment && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left 2 Columns: Video skeleton display & Gait features */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Visual Canvas Box */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-extrabold text-slate-800 dark:text-white text-base">MediaPipe Pose Estimator</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">33 body-node coordinate mesh | Session #{selectedAssessment.session_number}</p>
                </div>
                <div className="text-xs font-bold text-slate-400 flex items-center space-x-1.5">
                  <Calendar className="w-4 h-4" />
                  <span>{new Date(selectedAssessment.assessment_date).toLocaleDateString()}</span>
                </div>
              </div>
              
              {/* Skeleton overlay component */}
              <SkeletonViewer 
                landmarks={selectedAssessment.extracted_features?.landmarks} 
                affectedSide={patient.affected_side}
              />
            </div>

            {/* Extracted Gait Parameters & Joint angles metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Gait parameters */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
                <h4 className="font-extrabold text-xs text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-0.5">
                  Gait Metrics
                </h4>
                
                <div className="space-y-3.5 text-xs">
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Relative Walking Speed</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.gait.walking_speed_ms} Index</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Stride Length</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.gait.stride_length_m} m</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Cadence</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.gait.cadence_steps_min} steps/min</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Step Symmetry Ratio</span>
                    <span className="font-bold text-red-500">{selectedAssessment.extracted_features?.gait.step_symmetry_ratio}</span>
                  </div>
                  <div className="flex justify-between pb-1">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Step Width</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.gait.step_width_m} m</span>
                  </div>
                </div>
              </div>

              {/* Joint angles */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
                <h4 className="font-extrabold text-xs text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-0.5">
                  Joint Range of Motion
                </h4>
                
                <div className="space-y-3.5 text-xs">
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Knee Flexion (max)</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.angles.knee_angle_deg}°</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Hip Extension (max)</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.angles.hip_angle_deg}°</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Shoulder Mobility</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.angles.shoulder_angle_deg}°</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Elbow Flexion</span>
                    <span className="font-bold text-slate-800 dark:text-white">{selectedAssessment.extracted_features?.angles.elbow_angle_deg}°</span>
                  </div>
                  <div className="flex justify-between pb-1">
                    <span className="text-slate-500 dark:text-slate-400 font-semibold">Balance Stability score</span>
                    <span className="font-bold text-teal-500">{selectedAssessment.extracted_features?.balance_stability_score}%</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Targeted Rehabilitation Prescriptions */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                    <Dumbbell className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-slate-800 dark:text-white text-base">
                      Prescribed Rehabilitation Program
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Evidence-based exercise protocols tailored to detected kinematic deficits
                    </p>
                  </div>
                </div>
                <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1 bg-teal-500/10 text-teal-600 dark:text-teal-400 rounded-full text-[10px] font-bold">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Clinical Decision Support</span>
                </div>
              </div>

              {selectedAssessment.prescribed_exercises && selectedAssessment.prescribed_exercises.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  {selectedAssessment.prescribed_exercises.map((ex, idx) => {
                    const isLower = ex.category.includes('Lower') || ex.category.includes('Pelvic') || ex.category.includes('Core');
                    const isUpper = ex.category.includes('Upper');
                    const isGait = ex.category.includes('Gait');
                    const isBalance = ex.category.includes('Balance');
                    
                    const catBg = isLower ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20' :
                                  isUpper ? 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20' :
                                  isGait ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' :
                                  isBalance ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20' :
                                  'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';

                    return (
                      <div 
                        key={idx}
                        className="bg-slate-50 dark:bg-slate-800/40 border border-slate-200/70 dark:border-slate-800 rounded-2xl p-4 space-y-3 hover:border-primary/40 transition-colors"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-1">
                            <span className={`inline-block px-2.5 py-0.5 rounded-full text-[9px] font-extrabold border ${catBg}`}>
                              {ex.category}
                            </span>
                            <h4 className="font-extrabold text-slate-800 dark:text-white text-xs leading-snug">
                              {ex.title}
                            </h4>
                          </div>
                          <span className="text-[9px] font-bold px-2 py-0.5 bg-slate-200/80 dark:bg-slate-700/80 text-slate-700 dark:text-slate-300 rounded-md flex-shrink-0">
                            {ex.intensity}
                          </span>
                        </div>

                        {/* Deficit Callout */}
                        <div className="flex items-center space-x-1.5 text-[10px] text-rose-500 dark:text-rose-400 font-semibold bg-rose-500/5 dark:bg-rose-500/10 px-2.5 py-1.5 rounded-lg border border-rose-500/10">
                          <Target className="w-3.5 h-3.5 flex-shrink-0" />
                          <span>Deficit: {ex.target_deficit}</span>
                        </div>

                        {/* Dosage */}
                        <div className="flex items-center space-x-1.5 text-[10px] text-slate-700 dark:text-slate-300 font-bold bg-white dark:bg-slate-900/80 px-2.5 py-1.5 rounded-lg border border-slate-200/60 dark:border-slate-800">
                          <Clock className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                          <span>Dosage: {ex.dosage}</span>
                        </div>

                        {/* Instructions */}
                        <p className="text-[10px] text-slate-600 dark:text-slate-400 leading-relaxed">
                          {ex.instructions}
                        </p>

                        {/* Clinical Rationale */}
                        <div className="pt-1.5 border-t border-slate-200/60 dark:border-slate-800/80 flex items-start space-x-1.5 text-[9px] text-slate-500 dark:text-slate-400">
                          <Zap className="w-3 h-3 text-amber-500 mt-0.5 flex-shrink-0" />
                          <span><b>Clinical Rationale:</b> {ex.clinical_rationale}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="space-y-2">
                  {selectedAssessment.recommendations.map((rec, i) => (
                    <div key={i} className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* Right 1 Column: ML Prediction details & Clinical Scores */}
          <div className="space-y-6">
            
            {/* ML prediction card */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-5">
              <div>
                <h4 className="font-extrabold text-slate-800 dark:text-white text-sm">AI Movement Analysis</h4>
                <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">Machine Learning classifier decision</p>
              </div>

              {/* Large impairment counter */}
              <div className="text-center p-5 bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-slate-100 dark:border-slate-800">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block">Predicted Level</span>
                <span className={`text-xl font-extrabold block mt-2 ${
                  selectedAssessment.predictions.impairment_level === 'Normal' ? 'text-emerald-500' :
                  selectedAssessment.predictions.impairment_level === 'Mild' ? 'text-blue-500' :
                  selectedAssessment.predictions.impairment_level === 'Moderate' ? 'text-amber-500' :
                  'text-rose-500'
                }`}>
                  {selectedAssessment.predictions.impairment_level}
                </span>
                
                {selectedAssessment.predictions.confidence !== undefined && (
                  <div className="flex items-center justify-center space-x-1.5 mt-3 text-[10px] text-slate-500">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Confidence: <span className="font-bold">{Math.round(selectedAssessment.predictions.confidence * 100)}%</span></span>
                  </div>
                )}
              </div>

              {/* Feature importance weights */}
              <div className="space-y-2">
                <h5 className="font-bold text-[10px] text-slate-400 uppercase tracking-wider pl-0.5">Feature Importance Weights</h5>
                {selectedAssessment.predictions.feature_importances ? (
                  <div className="space-y-2">
                    {Object.entries(selectedAssessment.predictions.feature_importances).slice(0, 4).map(([name, val]) => (
                      <div key={name} className="space-y-1">
                        <div className="flex justify-between text-[10px] font-semibold text-slate-600 dark:text-slate-400 capitalize">
                          <span>{name.replace('_', ' ')}</span>
                          <span>{Math.round(val * 100)}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary rounded-full"
                            style={{ width: `${val * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[10px] text-slate-400 font-medium italic p-2 bg-slate-50 dark:bg-slate-800/30 rounded-lg">
                    Feature importances are not available for non-tree models (e.g., SVM).
                  </p>
                )}
              </div>
            </div>

            {/* Clinical scores comparison card */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
              <h4 className="font-extrabold text-slate-800 dark:text-white text-sm">Clinician-Entered Assessment Scores</h4>
              
              <div className="space-y-3.5 text-xs">
                <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                  <span className="text-slate-500 dark:text-slate-400 font-semibold">FMA Score</span>
                  <span className="font-bold text-slate-800 dark:text-white">
                    {selectedAssessment.clinical_scores.fma_score > 0 ? `${selectedAssessment.clinical_scores.fma_score} /226` : 'Not provided'}
                  </span>
                </div>
                <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                  <span className="text-slate-500 dark:text-slate-400 font-semibold">BBS Score</span>
                  <span className="font-bold text-slate-800 dark:text-white">
                    {selectedAssessment.clinical_scores.bbs_score > 0 ? `${selectedAssessment.clinical_scores.bbs_score} /56` : 'Not provided'}
                  </span>
                </div>
                <div className="flex justify-between border-b border-slate-50 dark:border-slate-800/80 pb-2">
                  <span className="text-slate-500 dark:text-slate-400 font-semibold">TUG Score</span>
                  <span className="font-bold text-slate-800 dark:text-white">
                    {selectedAssessment.clinical_scores.tug_score > 0 ? `${selectedAssessment.clinical_scores.tug_score}s` : 'Not provided'}
                  </span>
                </div>
                
                {/* Visual score comparison HUD */}
                <div className="pt-2">
                  <div className="flex justify-between font-bold text-[10px] uppercase text-slate-400 mb-2">
                    <span>Clinical Score</span>
                    <span>AI Predicted</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div className="p-3 bg-blue-500/5 dark:bg-blue-500/10 rounded-xl border border-blue-500/10">
                      <span className="text-lg font-black text-blue-600 dark:text-blue-400">
                        {selectedAssessment.clinical_scores.overall_clinical_score > 0 ? `${selectedAssessment.clinical_scores.overall_clinical_score}%` : 'N/A'}
                      </span>
                      <p className="text-[8px] font-bold text-slate-400 uppercase mt-0.5">Validation</p>
                    </div>
                    
                    <div className="p-3 bg-teal-500/5 dark:bg-teal-500/10 rounded-xl border border-teal-500/10">
                      <span className="text-lg font-black text-teal-600 dark:text-teal-400">
                        {selectedAssessment.predictions.impairment_level === 'Normal' ? '98%' :
                         selectedAssessment.predictions.impairment_level === 'Mild' ? '85%' :
                         selectedAssessment.predictions.impairment_level === 'Moderate' ? '60%' :
                         selectedAssessment.predictions.impairment_level === 'Severe' ? '35%' :
                         selectedAssessment.predictions.impairment_level === 'Very Severe' ? '15%' : 'N/A'}
                      </span>
                      <p className="text-[8px] font-bold text-slate-400 uppercase mt-0.5">Objective</p>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            {/* Recommendations card */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
              <h4 className="font-extrabold text-slate-800 dark:text-white text-sm">Physiotherapeutic Decision Support</h4>
              
              <div className="space-y-3">
                {selectedAssessment.recommendations.map((rec, i) => {
                  const isDisclaimer = rec.includes("qualified healthcare professionals");
                  return (
                    <div 
                      key={i} 
                      className={`p-3 rounded-xl text-[10px] leading-relaxed font-semibold flex items-start space-x-2.5 ${
                        isDisclaimer 
                          ? 'bg-rose-500/5 border border-rose-500/10 text-rose-600 dark:text-rose-400' 
                          : 'bg-slate-50 dark:bg-slate-800/40 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      <CheckCircle className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${isDisclaimer ? 'text-rose-500' : 'text-primary'}`} />
                      <span>{rec}</span>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Scientific Limitation & Clinical Disclaimer */}
      <div className="p-4 bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 rounded-2xl text-xs font-medium leading-relaxed flex items-start space-x-3 mt-8">
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <span>
          <strong>Scientific Limitation & Clinical Disclaimer:</strong> This system provides movement analysis and machine-learning predictions for research/rehabilitation support. It does not provide a medical diagnosis. Clinical assessments must be performed and interpreted by qualified healthcare professionals.
        </span>
      </div>

    </div>
  );
};
export default PatientProfile;
