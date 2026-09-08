import React from 'react';
import { 
  BookOpen, 
  Cpu, 
  Activity, 
  ShieldCheck, 
  Layers, 
  CheckCircle, 
  AlertTriangle, 
  BarChart2, 
  FileText,
  Zap,
  Target
} from 'lucide-react';

export const Methodology: React.FC = () => {
  return (
    <div className="space-y-8 font-sans max-w-6xl mx-auto pb-12">
      
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-700 via-primary to-teal-600 text-white p-8 rounded-3xl shadow-lg space-y-4">
        <div className="flex items-center space-x-3 text-blue-200 text-xs font-extrabold uppercase tracking-widest">
          <BookOpen className="w-4 h-4" />
          <span>IEEE Research & Biomechanical Methodology Specification</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black leading-tight">
          Machine Learning-Based Gait and Upper Limb Motor Impairment Analysis for Stroke Rehabilitation
        </h1>
        <p className="text-xs md:text-sm text-blue-100/90 leading-relaxed max-w-4xl">
          An end-to-end computer vision and machine learning framework for markerless 3D pose extraction, peak-based gait dynamic evaluation, 12-dimensional biomechanical feature representation, and subject-independent stroke rehabilitation movement pattern classification.
        </p>
      </div>

      {/* Methodological Overview Pipeline */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-slate-800 dark:text-white">Processing Architecture & Pipeline</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Pure markerless video input to subject-independent ML classification</p>
          </div>
        </div>

        {/* Workflow Diagram */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-2">
          
          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2 text-center">
            <span className="w-7 h-7 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center mx-auto">1</span>
            <h4 className="font-extrabold text-slate-800 dark:text-white text-xs">Video QC Input</h4>
            <p className="text-[10px] text-slate-500">Frame resolution, FPS, lighting, and full-body visibility classification.</p>
          </div>

          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2 text-center">
            <span className="w-7 h-7 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center mx-auto">2</span>
            <h4 className="font-extrabold text-slate-800 dark:text-white text-xs">MediaPipe Landmark</h4>
            <p className="text-[10px] text-slate-500">33-keypoint 3D anatomical body coordinate tracking across temporal sequences.</p>
          </div>

          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2 text-center">
            <span className="w-7 h-7 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center mx-auto">3</span>
            <h4 className="font-extrabold text-slate-800 dark:text-white text-xs">Peak Step Detection</h4>
            <p className="text-[10px] text-slate-500">Locates heel strikes via local minima of ankle y-coordinates for temporal step segmentation.</p>
          </div>

          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2 text-center">
            <span className="w-7 h-7 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center mx-auto">4</span>
            <h4 className="font-extrabold text-slate-800 dark:text-white text-xs">12-D Feature Vector</h4>
            <p className="text-[10px] text-slate-500">Calculates normalized relative spatial indices, sagittal ROM angles, and stability scores.</p>
          </div>

          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2 text-center">
            <span className="w-7 h-7 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center mx-auto">5</span>
            <h4 className="font-extrabold text-slate-800 dark:text-white text-xs font-sans">Subject-Free ML</h4>
            <p className="text-[10px] text-slate-500">GroupKFold validation across 71 subjects yielding probability breakdown P(c).</p>
          </div>

        </div>
      </div>

      {/* 12 Biomechanical Feature Specifications Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-teal-500/10 flex items-center justify-center text-teal-600 dark:text-teal-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-slate-800 dark:text-white">12-Dimensional Biomechanical Feature Representations</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Mathematically defensible parameters for monocular video input</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 dark:text-slate-500 uppercase tracking-widest font-extrabold">
                <th className="pb-3 pl-2">Feature Symbol</th>
                <th className="pb-3">Metric Name</th>
                <th className="pb-3">Dimension / Unit</th>
                <th className="pb-3">Mathematical Definition</th>
                <th className="pb-3">Clinical Relevance in Stroke</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">hip_angle_deg</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Hip Sagittal ROM</td>
                <td className="py-3 text-slate-500">Degrees (°)</td>
                <td className="py-3 text-slate-500">Max - Min angle between Shoulder-Hip-Knee vector</td>
                <td className="py-3 text-slate-500">Measures pelvic control & forward stride propulsion</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">peak_knee_flexion_deg</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Peak Knee Flexion</td>
                <td className="py-3 text-slate-500">Degrees (°)</td>
                <td className="py-3 text-slate-500">180° - interior angle(Hip, Knee, Ankle)</td>
                <td className="py-3 text-slate-500">Crucial for swing clearance; identifies stiff-knee gait</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">shoulder_mobility_deg</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Shoulder Swing ROM</td>
                <td className="py-3 text-slate-500">Degrees (°)</td>
                <td className="py-3 text-slate-500">Max - Min angle between Hip-Shoulder-Elbow vector</td>
                <td className="py-3 text-slate-500">Identifies bilateral arm swing reduction</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">elbow_flexion_deg</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Elbow Flexion Angle</td>
                <td className="py-3 text-slate-500">Degrees (°)</td>
                <td className="py-3 text-slate-500">Interior angle(Shoulder, Elbow, Wrist)</td>
                <td className="py-3 text-slate-500">Detects hemiparetic upper-limb flexor hypertonia</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">stride_length_index</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Relative Stride Length</td>
                <td className="py-3 text-slate-500">Unitless Index</td>
                <td className="py-3 text-slate-500">Mean peak-to-peak ankle stride / Leg Length</td>
                <td className="py-3 text-slate-500">Normalizes distance across uncalibrated cameras</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">cadence_steps_min</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Step Cadence</td>
                <td className="py-3 text-slate-500">steps/min</td>
                <td className="py-3 text-slate-500 font-mono">(Step Count / Duration sec) × 60</td>
                <td className="py-3 text-slate-500">Evaluates temporal walking rhythm frequency</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">walking_speed_index</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Relative Walking Speed</td>
                <td className="py-3 text-slate-500">Unitless Index</td>
                <td className="py-3 text-slate-500 font-mono">(Stride Index × Cadence) / 120</td>
                <td className="py-3 text-slate-500">Primary functional mobility indicator</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">step_width_index</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Relative Step Width</td>
                <td className="py-3 text-slate-500">Unitless Index</td>
                <td className="py-3 text-slate-500 font-mono font-xs">|x_L - x_R| / Hip Width</td>
                <td className="py-3 text-slate-500">Measures base of support compensation for instability</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">step_symmetry_ratio</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Step Symmetry Ratio</td>
                <td className="py-3 text-slate-500">Ratio (0 - 1.0)</td>
                <td className="py-3 text-slate-500 font-mono font-xs">min(t_L, t_R) / max(t_L, t_R)</td>
                <td className="py-3 text-slate-500">Quantifies hemiparetic stance duration imbalance</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">arm_swing_deg</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Arm Swing Amplitude</td>
                <td className="py-3 text-slate-500">Degrees (°)</td>
                <td className="py-3 text-slate-500">Max sagittal wrist displacement angle</td>
                <td className="py-3 text-slate-500">Monitors inter-limb coordination recovery</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">rom_score</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Composite ROM Score</td>
                <td className="py-3 text-slate-500">Percentage (%)</td>
                <td className="py-3 text-slate-500 font-xs">Weighted average normalized joint excursions</td>
                <td className="py-3 text-slate-500">Overall motor range percentage</td>
              </tr>
              <tr>
                <td className="py-3 pl-2 font-mono font-bold text-primary">balance_stability_score</td>
                <td className="py-3 font-semibold text-slate-800 dark:text-slate-200">Balance Stability Score</td>
                <td className="py-3 text-slate-500">Percentage (%)</td>
                <td className="py-3 text-slate-500 font-xs">100 - (Lateral Trunk Sway / Width × 100)</td>
                <td className="py-3 text-slate-500">Measures trunk center-of-mass sway control</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Machine Learning Benchmark & GroupKFold Validation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-500/10 flex items-center justify-center text-purple-600 dark:text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Subject-Independent Validation</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">StrokeRehab Primary Dataset Protocol</p>
            </div>
          </div>

          <div className="space-y-3 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            <p>
              Traditional machine learning models often suffer from <strong>intra-subject data leakage</strong> when frames or trials from the same subject appear in both training and test splits, producing artificially inflated validation scores.
            </p>
            <p>
              In our research methodology, classifiers are trained on the <strong>StrokeRehab Dataset</strong> (71 participants: 51 stroke-impaired, 20 healthy control; 355 total ADL trials) with relative gait reference validation from the <strong>PhysioNet Multi-Gait Dataset</strong>. Models are evaluated using <strong>5-Fold StratifiedGroupKFold Cross-Validation</strong> grouped strictly by <code>subject_id</code> across all 71 unique subjects:
            </p>
            <ul className="space-y-1.5 pl-4 list-disc font-semibold text-slate-700 dark:text-slate-200">
              <li><strong>Logistic Regression</strong>: GroupKFold Acc = 99.43%, Macro F1 = 0.9946, Weighted F1 = 0.9944</li>
              <li><strong>Support Vector Machine (SVM)</strong>: GroupKFold Acc = 99.14%, Macro F1 = 0.9918, Weighted F1 = 0.9916</li>
              <li><strong>Random Forest (100 Trees)</strong>: GroupKFold Acc = 98.57%, Macro F1 = 0.9864, Weighted F1 = 0.9859</li>
              <li><strong>XGBoost Classifier</strong>: GroupKFold Acc = 96.34%, Macro F1 = 0.9644, Weighted F1 = 0.9633</li>
            </ul>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 p-6 rounded-3xl shadow-sm space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-amber-500/10 flex items-center justify-center text-amber-600 dark:text-amber-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-800 dark:text-white text-base">Target StrokeRehab Pattern Classes</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">Ground-truth motor impairment categories</p>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <span className="font-bold text-emerald-600 dark:text-emerald-400 block">1. Healthy-like Movement Pattern</span>
              <span className="text-slate-600 dark:text-slate-400 text-[11px]">Symmetric stance duration, knee flexion &gt; 55°, speed index &gt; 1.0, balance stability &gt; 85%.</span>
            </div>

            <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl">
              <span className="font-bold text-purple-600 dark:text-purple-400 block">2. Restricted / Asymmetric Movement Pattern</span>
              <span className="text-slate-600 dark:text-slate-400 text-[11px]">Upper-limb flexor hypertonia (elbow angle &lt; 110°), reduced shoulder mobility (&lt; 20°), and asymmetric stride timing.</span>
            </div>

            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl">
              <span className="font-bold text-rose-600 dark:text-rose-400 block">3. Unstable Gait / Stance Pattern</span>
              <span className="text-slate-600 dark:text-slate-400 text-[11px]">Elevated lateral trunk sway, balance stability score &lt; 60%, wide base of support index, elevated risk of postural instability.</span>
            </div>
          </div>
        </div>

      </div>

      {/* Disclaimers */}
      <div className="p-5 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-3xl text-xs text-slate-600 dark:text-slate-300 leading-relaxed flex items-start space-x-3">
        <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-slate-800 dark:text-white mb-1">Ethical & Research Decision-Support Mandate</h4>
          <p>
            This system provides objective movement and gait analysis to assist physical therapists and clinical researchers. It does NOT make medical diagnoses or replace clinical judgment. All outputs must be verified by licensed healthcare professionals.
          </p>
        </div>
      </div>

    </div>
  );
};

export default Methodology;
