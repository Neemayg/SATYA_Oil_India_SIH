export type ObservationType = 'START' | 'PROGRESS' | 'FINISH' | 'HOLD' | 'QA_CLEARANCE' | 'INSPECTION';
export type Discipline = 'CIVIL' | 'PIPING' | 'STRUCTURAL' | 'MECHANICAL' | 'ELECTRICAL' | 'INSTRUMENTATION' | 'QA_QC' | 'SAFETY_HSE';
export type SyncStatus = 'PENDING' | 'SYNCED' | 'FAILED';

export interface Observation {
  id: string;
  projectId: string;
  activityId?: string;
  type: ObservationType;
  discipline: Discipline;
  location: string;
  quantity?: string;
  unit?: string;
  statement: string;
  photoUri?: string;
  audioUri?: string;
  observedAt: string;
  createdAt: string;
  syncStatus: SyncStatus;
  syncError?: string;
  serverSourceId?: string;
  eventsExtracted?: number;
}

export interface Settings {
  serverUrl: string;
  projectId: string;
  author: string;
}
