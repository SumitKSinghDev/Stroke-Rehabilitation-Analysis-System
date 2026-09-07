// API Client for Stroke Rehab Decision Support System

const BASE_URL = ''; // Proxied via Vite config to http://localhost:8000

export interface User {
  _id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'Admin' | 'Physiotherapist' | 'Doctor' | 'Patient';
  created_at?: string;
}

export interface Patient {
  _id: string;
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  stroke_type: 'Ischemic' | 'Hemorrhagic' | 'TIA';
  affected_side: 'Left' | 'Right' | 'Bilateral';
  stroke_date: string;
  current_status: 'Improving' | 'Stable' | 'Deteriorating';
  medical_notes?: string;
  photo_url?: string;
  therapist_id?: string;
  created_at?: string;
  session_count?: number;
}

export interface JointAngles {
  hip_angle_deg: number;
  knee_angle_deg: number;
  shoulder_angle_deg: number;
  elbow_angle_deg: number;
}

export interface GaitParameters {
  stride_length_m: number;
  cadence_steps_min: number;
  walking_speed_ms: number;
  step_width_m: number;
  step_symmetry_ratio: number;
}

export interface Landmark {
  id: number;
  x: number;
  y: number;
  z: number;
  visibility: number;
}

export interface MovementFeatures {
  angles: JointAngles;
  gait: GaitParameters;
  arm_swing_deg: number;
  rom_score: number;
  balance_stability_score: number;
  landmarks: Landmark[];
}

export interface MLPrediction {
  impairment_level: 'Normal' | 'Mild' | 'Moderate' | 'Severe' | 'Very Severe';
  model_used: string;
  confidence: number;
  feature_importances: Record<string, number>;
}

export interface ClinicalScores {
  fma_score: number;
  bbs_score: number;
  fac_score: number;
  tug_score: number;
  overall_clinical_score?: number;
}

export interface PrescribedExercise {
  title: string;
  category: string;
  target_deficit: string;
  dosage: string;
  intensity: string;
  instructions: string;
  clinical_rationale: string;
}

export interface Assessment {
  _id: string;
  patient_id: string;
  session_number: number;
  assessment_date: string;
  video_path?: string;
  clinical_scores: ClinicalScores;
  extracted_features: MovementFeatures;
  predictions: MLPrediction;
  recommendations: string[];
  prescribed_exercises?: PrescribedExercise[];
  therapist_notes?: string;
}

export interface ProgressTrendPoint {
  session_number: number;
  assessment_date: string;
  walking_speed: number;
  balance: number;
  hip_angle: number;
  knee_angle: number;
  shoulder_mobility: number;
  upper_limb_movement: number;
  overall_motor_score: number;
  impairment_level: string;
}

export interface ProgressComparisonMetric {
  initial: number;
  current: number;
  diff: number;
  improvement_pct: number;
}

export interface ProgressSummary {
  patient_id: string;
  name: string;
  session_count: number;
  improvement_pct: number;
  overall_status: string;
  recovery_timeline: ProgressTrendPoint[];
  recent_comparison: Record<string, ProgressComparisonMetric>;
}

export interface SystemLog {
  timestamp: string;
  level: string;
  user: string;
  action: string;
  details: string;
}

export interface AdminStats {
  total_users: number;
  total_patients: number;
  total_assessments: number;
  role_counts: Record<string, number>;
  recent_logs: SystemLog[];
}

// Token Helpers
export const getAuthToken = () => localStorage.getItem('rehab_token');
export const setAuthToken = (token: string) => localStorage.setItem('rehab_token', token);
export const clearAuthToken = () => {
  localStorage.removeItem('rehab_token');
  localStorage.removeItem('rehab_user');
};

export const getStoredUser = (): User | null => {
  const userStr = localStorage.getItem('rehab_user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

export const setStoredUser = (user: User) => {
  localStorage.setItem('rehab_user', JSON.stringify(user));
};

// Generic Fetch Request Wrapper
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearAuthToken();
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    throw new Error('Authentication expired. Please log in again.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API request failed with status ${response.status}`);
  }

  // Handle PDF file downloads
  if (response.headers.get('Content-Type')?.includes('application/pdf')) {
    return response as unknown as T;
  }

  return response.json();
}

export const api = {
  auth: {
    login: async (username: string, password: string): Promise<any> => {
      // Use OAuth2 Password request format
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const res = await fetch(`${BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
      });
      
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Login failed');
      }
      
      const data = await res.json();
      setAuthToken(data.access_token);
      
      // Fetch user profile
      const user = await request<User>('/api/auth/me');
      setStoredUser(user);
      return { token: data.access_token, user };
    },
    
    register: async (userData: any): Promise<User> => {
      return request<User>('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
    },
    
    getMe: async (): Promise<User> => {
      return request<User>('/api/auth/me');
    },
    
    updateProfile: async (profileData: any): Promise<User> => {
      return request<User>('/api/auth/me', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
      });
    },
    
    updatePassword: async (passwordData: any): Promise<any> => {
      return request<any>('/api/auth/me/password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(passwordData)
      });
    }
  },
  
  patients: {
    list: async (): Promise<Patient[]> => {
      return request<Patient[]>('/api/patients');
    },
    
    get: async (id: string): Promise<Patient> => {
      return request<Patient>(`/api/patients/${id}`);
    },
    
    create: async (patientData: Omit<Patient, '_id' | 'session_count'>): Promise<Patient> => {
      return request<Patient>('/api/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      });
    },
    
    update: async (id: string, patientData: Partial<Patient>): Promise<Patient> => {
      return request<Patient>(`/api/patients/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      });
    },
    
    delete: async (id: string): Promise<any> => {
      return request<any>(`/api/patients/${id}`, {
        method: 'DELETE'
      });
    }
  },
  
  assessments: {
    list: async (patientId?: string): Promise<Assessment[]> => {
      const url = patientId ? `/api/assessments?patient_id=${patientId}` : '/api/assessments';
      return request<Assessment[]>(url);
    },
    
    get: async (id: string): Promise<Assessment> => {
      return request<Assessment>(`/api/assessments/${id}`);
    },
    
    create: async (formData: FormData): Promise<Assessment> => {
      // Must not set Content-Type header manually for FormData so the browser sets the boundary correctly
      return request<Assessment>('/api/assessments', {
        method: 'POST',
        body: formData
      });
    },
    
    compare: async (patientId: string): Promise<any[]> => {
      return request<any[]>(`/api/assessments/compare/${patientId}`);
    },
    
    createDirect: async (assessmentData: any): Promise<Assessment> => {
      return request<Assessment>('/api/assessments/direct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessmentData)
      });
    }
  },
  
  progress: {
    get: async (patientId: string): Promise<ProgressSummary> => {
      return request<ProgressSummary>(`/api/progress/${patientId}`);
    }
  },
  
  admin: {
    getStats: async (): Promise<AdminStats> => {
      return request<AdminStats>('/api/admin/stats');
    },
    
    listUsers: async (): Promise<User[]> => {
      return request<User[]>('/api/admin/users');
    },
    
    updateUserRole: async (userId: string, newRole: string): Promise<User> => {
      return request<User>(`/api/admin/users/${userId}/role?new_role=${newRole}`, {
        method: 'PUT'
      });
    },
    
    deleteUser: async (userId: string): Promise<any> => {
      return request<any>(`/api/admin/users/${userId}`, {
        method: 'DELETE'
      });
    }
  },
  
  reports: {
    download: async (assessmentId: string, filename: string): Promise<void> => {
      const token = getAuthToken();
      const response = await fetch(`${BASE_URL}/api/reports/generate/${assessmentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to generate PDF report');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    }
  }
};
