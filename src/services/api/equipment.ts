import { Equipment } from '../../types/equipment';

// MOCK ADAPTER for Equipment API
// TODO: Replace with actual axios call to /api/equipment/:id when Backend is ready.
export const getEquipmentHealth = async (id: string): Promise<Equipment> => {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 800));

  // Mock data representing Pump P-101
  return {
    id: id || 'P-101',
    name: 'Pump P-101',
    status: 'Warning',
    healthScore: 72,
    metrics: {
      temperature: 92, // °C
      vibration: 6.8,  // mm/s
      pressure: 4.2,   // bar
    },
    issues: [
      { id: '1', description: 'High bearing temperature', riskLevel: 'High' },
      { id: '2', description: 'Increasing vibration', riskLevel: 'Medium' },
    ],
    aiRecommendation: 'Schedule maintenance within 48 hours to inspect bearings and re-align shaft. Vibration signatures match historical failure pattern for this pump type.',
  };
};
