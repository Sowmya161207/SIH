export type EquipmentStatus = 'Healthy' | 'Warning' | 'Critical';

export interface SensorMetrics {
  temperature: number;
  vibration: number;
  pressure: number;
}

export interface DetectedIssue {
  id: string;
  description: string;
  riskLevel: 'Low' | 'Medium' | 'High';
}

export interface Equipment {
  id: string;
  name: string;
  status: EquipmentStatus;
  healthScore: number; // 0 to 100
  metrics: SensorMetrics;
  issues: DetectedIssue[];
  aiRecommendation: string;
}
