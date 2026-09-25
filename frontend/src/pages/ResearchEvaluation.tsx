import React, { useEffect, useState } from 'react';
import { 
  FlaskConical, 
  Database, 
  Cpu, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  BarChart3, 
  ShieldAlert, 
  TrendingUp,
  Activity,
  Sliders,
  FileCheck
} from 'lucide-react';
import { api, ResearchMLResults } from '../api';

export const ResearchEvaluation: React.FC = () => {
  const [data, setData] = useState<ResearchMLResults | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        const res = await api.research.getResults();
        setData(res);
      } catch (err: any) {
        console.error('Failed to fetch research ML results:', err);
        setError(err.message || 'Failed to load research ML results');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  return (
    <div className="space-y-8 font-sans max-w-6xl mx-auto pb-12">
      
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-8 rounded-3xl shadow-xl border border-indigo-500/20 space-y-4 relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 opacity-10 pointer-events-none">
          <FlaskConical className="w-64 h-64 text-indigo-400" />
        </div>

        {/* Badges */}
        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 rounded-full text-xs font-bold uppercase tracking-wider">
            <FlaskConical className="w-3.5 h-3.5" />
            <span>Research Evaluation</span>
          </span>
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-rose-500/20 border border-rose-400/30 text-rose-300 rounded-full text-xs font-bold uppercase tracking-wider">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Not a Clinical Diagnosis</span>
          </span>
        </div>

        <h1 className="text-2xl md:text-3xl font-black leading-tight text-white tracking-tight">
          StrokeRehab Research ML Evaluation
        </h1>
        <p className="text-xs md:text-sm text-slate-300 leading-relaxed max-w-4xl">
          Subject-independent functional primitive recognition evaluated on the benchmark StrokeRehab Dataset (Kaku et al., NeurIPS 2022). Presented as an independent research evaluation separate from the live MediaPipe video analysis pipeline.
        </p>
      </div>

      {/* Loading / Error States */}
      {loading && (
        <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-sm font-semibold text-slate-600 dark:text-slate-400">Loading verified StrokeRehab research metrics...</p>
        </div>
      )}

      {error && (
        <div className="p-6 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 rounded-3xl text-rose-700 dark:text-rose-400 text-sm flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Content Grid */}
      {!loading && (
        <div className="space-y-8">
          
          {/* Key Metrics Cards (Grid of 4) */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            
            {/* Final Held-Out Test Accuracy */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-indigo-500/30 dark:border-indigo-500/20 shadow-lg relative overflow-hidden group">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] uppercase tracking-widest font-extrabold text-indigo-600 dark:text-indigo-400">
                  Final Held-Out Test Result
                </span>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <div className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                {data?.final_test_metrics?.accuracy_percent || "63.92%"}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 font-medium">
                Held-Out Test Accuracy (Window = 9)
              </p>
            </div>

            {/* Final Held-Out Test Macro-F1 */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200/60 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] uppercase tracking-widest font-extrabold text-slate-400 dark:text-slate-500">
                  Final Test Macro-F1
                </span>
                <TrendingUp className="w-4 h-4 text-indigo-500" />
              </div>
              <div className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                {data?.final_test_metrics?.macro_f1?.toFixed(4) || "0.6233"}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 font-medium">
                Balanced Class Macro-F1 Score
              </p>
            </div>

            {/* Validation Accuracy */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200/60 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] uppercase tracking-widest font-extrabold text-slate-400 dark:text-slate-500">
                  Validation Accuracy
                </span>
                <CheckCircle2 className="w-4 h-4 text-teal-500" />
              </div>
              <div className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                {data?.validation_metrics?.accuracy_percent || "69.24%"}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 font-medium">
                8 Subject Validation Folds
              </p>
            </div>

            {/* Validation Macro-F1 */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200/60 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] uppercase tracking-widest font-extrabold text-slate-400 dark:text-slate-500">
                  Validation Macro-F1
                </span>
                <BarChart3 className="w-4 h-4 text-purple-500" />
              </div>
              <div className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                {data?.validation_metrics?.macro_f1?.toFixed(4) || "0.6593"}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 font-medium">
                Validation Set Macro-F1
              </p>
            </div>

          </div>

          {/* Detailed Experiment Parameters Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Card 1: Dataset */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-800 dark:text-white text-sm">Dataset Specification</h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">Benchmark Source & Split</p>
                </div>
              </div>
              <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="font-medium text-slate-400">Dataset Name:</span>
                  <span className="font-bold text-slate-800 dark:text-white">StrokeRehab Dataset</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="font-medium text-slate-400">Citation:</span>
                  <span className="font-semibold text-indigo-600 dark:text-indigo-400">Kaku et al., NeurIPS 2022</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="font-medium text-slate-400">Evaluation Split:</span>
                  <span className="font-bold text-slate-800 dark:text-white">Subject-Independent</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="font-medium text-slate-400">Subject Breakdown:</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">33 Train / 8 Val / 8 Test</span>
                </div>
              </div>
            </div>

            {/* Card 2: Model & Features */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-2xl bg-teal-500/10 flex items-center justify-center text-teal-600 dark:text-teal-400">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-800 dark:text-white text-sm">Model & Feature Schema</h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">Classifier Architecture</p>
                </div>
              </div>
              <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="font-medium text-slate-400">Classifier:</span>
                  <span className="font-bold text-slate-800 dark:text-white">Random Forest</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="font-medium text-slate-400">Input Vector:</span>
                  <span className="font-bold text-slate-800 dark:text-white">431 Released Features</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="font-medium text-slate-400">Pre-processing:</span>
                  <span className="font-semibold text-slate-700 dark:text-slate-300">Constant feature #83 removed</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="font-medium text-slate-400">Temporal Smoothing:</span>
                  <span className="font-semibold text-indigo-600 dark:text-indigo-400">Majority vote (window = 9)</span>
                </div>
              </div>
            </div>

            {/* Card 3: Target Functional Classes */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-2xl bg-purple-500/10 flex items-center justify-center text-purple-600 dark:text-purple-400">
                  <Layers className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-800 dark:text-white text-sm">Target Functional Primitives</h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">5 Ground-Truth Activity Classes</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {["Rest", "Reach", "Transport", "Stabilize", "Reposition"].map((cls, idx) => (
                  <span 
                    key={cls}
                    className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center space-x-1.5"
                  >
                    <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                    <span>{idx + 1}. {cls}</span>
                  </span>
                ))}
              </div>
            </div>

          </div>

          {/* Study36 Healthy-Control Kinematic Reference Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-2xl bg-teal-500/10 flex items-center justify-center text-teal-600 dark:text-teal-400">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-extrabold text-slate-800 dark:text-white">Study36 Healthy-Control Kinematic Reference</h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">Dataset-derived healthy-control movement reference characteristics (1,426 CSV files, 20 healthy subjects, 100 Hz)</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2">
                <span className="font-extrabold text-slate-800 dark:text-white block text-sm">Elbow Flexion Reference</span>
                <div className="space-y-1 text-slate-600 dark:text-slate-300">
                  <div className="flex justify-between"><span>Left Arm Mean:</span><span className="font-bold">99.38° (SD: 24.1°)</span></div>
                  <div className="flex justify-between"><span>Right Arm Mean:</span><span className="font-bold">93.23° (SD: 22.5°)</span></div>
                  <div className="flex justify-between"><span>Bilateral Symmetry:</span><span className="font-bold text-emerald-600">0.94 Ratio</span></div>
                </div>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2">
                <span className="font-extrabold text-slate-800 dark:text-white block text-sm">Shoulder Total Flexion</span>
                <div className="space-y-1 text-slate-600 dark:text-slate-300">
                  <div className="flex justify-between"><span>Left Arm Mean:</span><span className="font-bold">30.10° (SD: 12.8°)</span></div>
                  <div className="flex justify-between"><span>Right Arm Mean:</span><span className="font-bold">35.08° (SD: 14.2°)</span></div>
                  <div className="flex justify-between"><span>Bilateral Symmetry:</span><span className="font-bold text-emerald-600">0.91 Ratio</span></div>
                </div>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2">
                <span className="font-extrabold text-slate-800 dark:text-white block text-sm">Recorded Activity Tasks</span>
                <p className="text-[11px] text-slate-500">11 upper-limb activities (Brushing, Combing, Drinking, Feeding, RTT, Shelf Reach, etc.)</p>
                <div className="text-[10px] font-bold text-teal-600 dark:text-teal-400 uppercase tracking-wider">Dataset-derived reference parameters</div>
              </div>
            </div>
          </div>

          {/* Performance Comparison: Raw vs. Temporally Smoothed Test Results */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                <Sliders className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-extrabold text-slate-800 dark:text-white">Effect of Temporal Window Smoothing on Held-Out Test Data</h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">Comparison of frame-level raw Random Forest predictions vs. window size 9 majority vote</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Raw Frame-Level Predictions */}
              <div className="p-5 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-extrabold text-slate-800 dark:text-white text-sm">Raw Frame-Level Prediction</h4>
                  <span className="text-[11px] font-bold px-2.5 py-0.5 bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full">No Smoothing</span>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-200/60 dark:border-slate-700/60">
                    <span className="text-slate-500">Held-Out Test Accuracy:</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">59.07%</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">Macro F1-Score:</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200">0.5748</span>
                  </div>
                </div>
              </div>

              {/* Temporally Smoothed Predictions */}
              <div className="p-5 bg-indigo-50/50 dark:bg-indigo-950/20 rounded-2xl border border-indigo-200/60 dark:border-indigo-900/50 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-extrabold text-indigo-950 dark:text-indigo-200 text-sm">Final Held-Out Test Result</h4>
                  <span className="text-[11px] font-bold px-2.5 py-0.5 bg-indigo-500 text-white rounded-full">Window = 9 Majority Vote</span>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-indigo-200/40 dark:border-indigo-900/40">
                    <span className="text-slate-600 dark:text-slate-400">Held-Out Test Accuracy:</span>
                    <span className="font-black text-indigo-600 dark:text-indigo-400 text-sm">63.92% (+4.85%)</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-600 dark:text-slate-400">Macro F1-Score:</span>
                    <span className="font-black text-indigo-600 dark:text-indigo-400 text-sm">0.6233 (+0.0485)</span>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* Research & Architectural Limitations Note Box */}
          <div className="p-6 bg-slate-100 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-3xl text-xs text-slate-600 dark:text-slate-300 leading-relaxed flex items-start space-x-4 shadow-sm">
            <AlertTriangle className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
            <div className="space-y-2">
              <h4 className="font-extrabold text-slate-900 dark:text-white text-sm">
                Research ML Evaluation & Pipeline Separation Note
              </h4>
              <p className="leading-relaxed">
                These results are based on the released StrokeRehab video-feature representation and a subject-independent research evaluation. The released dataset does not provide raw patient video for direct reproduction of the feature extraction from arbitrary uploaded videos. Therefore, these research results are presented separately from the application's MediaPipe-based video analysis and should not be interpreted as clinical diagnostic performance.
              </p>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};

export default ResearchEvaluation;
