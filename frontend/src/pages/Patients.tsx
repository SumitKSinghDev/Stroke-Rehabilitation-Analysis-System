import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  Search, 
  Plus, 
  Activity, 
  Calendar, 
  UserCircle,
  X,
  Loader2,
  FileSpreadsheet
} from 'lucide-react';
import { api, Patient } from '../api';

export const Patients: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [strokeFilter, setStrokeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  // Form fields
  const [patientId, setPatientId] = useState('');
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');
  const [strokeType, setStrokeType] = useState('Ischemic');
  const [affectedSide, setAffectedSide] = useState('Right');
  const [strokeDate, setStrokeDate] = useState('');
  const [currentStatus, setCurrentStatus] = useState('Stable');
  const [medicalNotes, setMedicalNotes] = useState('');

  const navigate = useNavigate();

  const fetchPatients = async () => {
    try {
      const data = await api.patients.list();
      setPatients(data);
    } catch (err) {
      console.error('Error loading patients:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleRegisterPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientId || !name || !age || !strokeDate) {
      setError('Please fill in all required fields.');
      return;
    }

    setSubmitting(true);
    setError('');

    const newPatient = {
      patient_id: patientId,
      name,
      age: parseInt(age),
      gender,
      stroke_type: strokeType as any,
      affected_side: affectedSide as any,
      stroke_date: strokeDate,
      current_status: currentStatus as any,
      medical_notes: medicalNotes,
    };

    try {
      await api.patients.create(newPatient);
      setIsModalOpen(false);
      
      // Reset form
      setPatientId('');
      setName('');
      setAge('');
      setStrokeDate('');
      setMedicalNotes('');
      
      // Refresh list
      fetchPatients();
    } catch (err: any) {
      setError(err.message || 'Registration failed. Check if Patient ID is unique.');
    } finally {
      setSubmitting(false);
    }
  };

  // Filter list
  const filteredPatients = patients.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) || 
                          p.patient_id.toLowerCase().includes(search.toLowerCase());
    const matchesStroke = strokeFilter ? p.stroke_type === strokeFilter : true;
    const matchesStatus = statusFilter ? p.current_status === statusFilter : true;
    
    return matchesSearch && matchesStroke && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Improving': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'Stable': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'Deteriorating': return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
      default: return 'bg-slate-500/10 text-slate-500 border-slate-500/20';
    }
  };

  return (
    <div className="space-y-8 font-sans">
      
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white tracking-tight">Patient Directory</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Clinical profiles and rehabilitation diagnostic reports.
          </p>
        </div>
        <button
          onClick={() => {
            // Generate simple unique ID
            const year = new Date().getFullYear();
            const rand = Math.floor(1000 + Math.random() * 9000);
            setPatientId(`PT-${year}-${rand}`);
            setIsModalOpen(true);
          }}
          className="flex items-center space-x-2 px-5 py-2.5 bg-primary text-white text-xs font-bold rounded-xl shadow-md hover:bg-primary/95 transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <Plus className="w-4.5 h-4.5 stroke-[2.5]" />
          <span>Register New Patient</span>
        </button>
      </div>

      {/* Filter and Search HUD */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        
        {/* Search */}
        <div className="relative w-full md:w-96">
          <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-400">
            <Search className="w-4 h-4" />
          </span>
          <input
            type="text"
            placeholder="Search by name or Patient ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 rounded-xl text-xs text-slate-700 dark:text-white focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 w-full md:w-auto">
          <select
            value={strokeFilter}
            onChange={(e) => setStrokeFilter(e.target.value)}
            className="px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 rounded-xl text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-primary cursor-pointer"
          >
            <option value="">All Stroke Types</option>
            <option value="Ischemic">Ischemic</option>
            <option value="Hemorrhagic">Hemorrhagic</option>
            <option value="TIA">Transient Ischemic (TIA)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 rounded-xl text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-primary cursor-pointer"
          >
            <option value="">All Rehab Statuses</option>
            <option value="Improving">Improving</option>
            <option value="Stable">Stable</option>
            <option value="Deteriorating">Deteriorating</option>
          </select>
        </div>

      </div>

      {/* Grid of Patient Cards */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
          ))}
        </div>
      ) : filteredPatients.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPatients.map((p) => (
            <div
              key={p._id}
              onClick={() => navigate(`/patients/${p.patient_id}`)}
              className="bg-white hover:bg-slate-50/50 dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition-all duration-200 hover:scale-[1.01] flex flex-col justify-between"
            >
              
              {/* Header profile block */}
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3.5">
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-primary border border-primary/20">
                      <UserCircle className="w-8 h-8 stroke-[1.5]" />
                    </div>
                    <div>
                      <h3 className="font-extrabold text-slate-800 dark:text-white text-base group-hover:text-primary transition-colors leading-snug">
                        {p.name}
                      </h3>
                      <span className="text-[10px] font-bold text-slate-400 tracking-wider block mt-0.5">
                        {p.patient_id}
                      </span>
                    </div>
                  </div>

                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getStatusColor(p.current_status)}`}>
                    {p.current_status}
                  </span>
                </div>

                {/* Patient stats */}
                <div className="grid grid-cols-2 gap-4 mt-6 pt-5 border-t border-slate-100 dark:border-slate-800 text-xs">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Age / Gender</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300 mt-1 block">{p.age} yrs / {p.gender}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Affected Side</span>
                    <span className="font-bold text-red-500 mt-1 block">{p.affected_side} Hand/Foot</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Stroke Type</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300 mt-1 block">{p.stroke_type}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Stroke Date</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300 mt-1 block flex items-center space-x-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400 mr-1" />
                      <span>{p.stroke_date}</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="bg-slate-50 dark:bg-slate-800/40 px-6 py-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center space-x-1.5 text-slate-500 dark:text-slate-400">
                  <Activity className="w-4 h-4 text-primary" />
                  <span className="font-bold text-[10px] uppercase tracking-wider">Sessions logged</span>
                </div>
                <span className="w-6 h-6 bg-primary/10 dark:bg-primary/20 text-primary font-extrabold rounded-full flex items-center justify-center text-xs">
                  {p.session_count || 0}
                </span>
              </div>

            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-12 text-center rounded-2xl">
          <Users className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto mb-4" />
          <p className="text-slate-500 dark:text-slate-400 font-semibold text-sm">No patient profiles match the query filters.</p>
        </div>
      )}

      {/* Register Patient Slide-over Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl animate-in zoom-in-95 duration-150">
            
            {/* Header */}
            <div className="px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-primary" />
                <h3 className="font-extrabold text-slate-800 dark:text-white text-base">New Patient Registration</h3>
              </div>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleRegisterPatient} className="p-6 space-y-4">
              {error && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-500 rounded-xl text-xs font-bold">
                  {error}
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                {/* Patient ID (Read-only generated) */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Patient ID (Auto)</label>
                  <input
                    type="text"
                    value={patientId}
                    readOnly
                    className="w-full px-4 py-2.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-500"
                  />
                </div>

                {/* Name */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Patient Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="Enter full name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                {/* Age */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Age *</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="120"
                    placeholder="E.g., 55"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20"
                  />
                </div>

                {/* Gender */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Gender</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                {/* Affected Side */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Affected Side</label>
                  <select
                    value={affectedSide}
                    onChange={(e) => setAffectedSide(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-red-500 font-bold focus:outline-none focus:border-primary"
                  >
                    <option value="Right">Right Hand/Foot</option>
                    <option value="Left">Left Hand/Foot</option>
                    <option value="Bilateral">Bilateral</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Stroke Type */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Stroke Category</label>
                  <select
                    value={strokeType}
                    onChange={(e) => setStrokeType(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                  >
                    <option value="Ischemic">Ischemic Stroke</option>
                    <option value="Hemorrhagic">Hemorrhagic Stroke</option>
                    <option value="TIA">Transient Ischemic (TIA)</option>
                  </select>
                </div>

                {/* Stroke Date */}
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Stroke Onset Date *</label>
                  <input
                    type="date"
                    required
                    value={strokeDate}
                    onChange={(e) => setStrokeDate(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              {/* Current Status */}
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Rehab Status</label>
                <select
                  value={currentStatus}
                  onChange={(e) => setCurrentStatus(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white focus:outline-none focus:border-primary"
                >
                  <option value="Stable">Stable</option>
                  <option value="Improving">Improving</option>
                  <option value="Deteriorating">Deteriorating</option>
                </select>
              </div>

              {/* Medical Notes */}
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 pl-0.5">Clinical Diagnoses / Notes</label>
                <textarea
                  rows={3}
                  placeholder="History of hemiplegia, spatial balance deficits, cane usage..."
                  value={medicalNotes}
                  onChange={(e) => setMedicalNotes(e.target.value)}
                  className="w-full px-4 py-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-white placeholder-slate-400 focus:outline-none focus:border-primary resize-none"
                />
              </div>

              {/* Submit Buttons */}
              <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2.5 border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-800"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-primary text-white rounded-xl text-xs font-bold shadow-md hover:bg-primary/95 flex items-center space-x-1.5"
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Saving Profile...</span>
                    </>
                  ) : (
                    <span>Register Profile</span>
                  )}
                </button>
              </div>

            </form>
          </div>
        </div>
      )}

    </div>
  );
};
export default Patients;
