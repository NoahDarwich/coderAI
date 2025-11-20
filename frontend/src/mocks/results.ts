/**
 * Mock Extraction Results Data
 * Sample extraction results for testing
 */

import { ExtractionResult, ExtractionDataPoint } from '@/lib/types/api';

/**
 * Generate random confidence score
 */
function randomConfidence(min: number = 70, max: number = 100): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generate mock extraction results for climate protests project
 */
export const mockExtractionResults: ExtractionResult[] = [
  {
    id: 'result-001',
    documentId: 'doc-001',
    documentName: 'london_climate_protest_jan2023.pdf',
    schemaId: 'schema-001',
    data: {
      protest_date: { value: '2023-01-15', confidence: 98, sourceText: 'On January 15, 2023, protesters gathered...' },
      city: { value: 'London', confidence: 100, sourceText: 'London city center' },
      country: { value: 'United Kingdom', confidence: 100, sourceText: 'London, UK' },
      participant_count: { value: 15000, confidence: 85, sourceText: 'approximately 15,000 demonstrators' },
      protest_topic: { value: 'Climate policy', confidence: 92, sourceText: 'demanding stronger climate action legislation' },
      violence_occurred: { value: 'No', confidence: 95, sourceText: 'peaceful demonstration' },
      police_response: { value: 'Observation only', confidence: 90, sourceText: 'police monitored from distance' },
    },
    flagged: false,
    extractedAt: '2024-01-16T09:00:00Z',
  },
  {
    id: 'result-002',
    documentId: 'doc-002',
    documentName: 'berlin_extinction_rebellion_march.pdf',
    schemaId: 'schema-001',
    data: {
      protest_date: { value: '2023-02-03', confidence: 96 },
      city: { value: 'Berlin', confidence: 100 },
      country: { value: 'Germany', confidence: 100 },
      participant_count: { value: 8500, confidence: 78, sourceText: 'between 7,000 and 10,000 people' },
      protest_topic: { value: 'Fossil fuels', confidence: 88 },
      violence_occurred: { value: 'No', confidence: 93 },
      police_response: { value: 'Crowd control', confidence: 87, sourceText: 'police established barriers' },
    },
    flagged: false,
    extractedAt: '2024-01-16T09:05:00Z',
  },
  {
    id: 'result-003',
    documentId: 'doc-003',
    documentName: 'paris_climate_strike_report.docx',
    schemaId: 'schema-001',
    data: {
      protest_date: { value: '2023-03-10', confidence: 99 },
      city: { value: 'Paris', confidence: 100 },
      country: { value: 'France', confidence: 100 },
      participant_count: { value: 25000, confidence: 82 },
      protest_topic: { value: 'Climate policy', confidence: 95 },
      violence_occurred: { value: 'Yes', confidence: 85, sourceText: 'minor clashes with police, some property damage' },
      police_response: { value: 'Arrests made', confidence: 91, sourceText: '23 arrests were reported' },
    },
    flagged: true,
    reviewNotes: 'Low confidence on participant count - needs verification',
    extractedAt: '2024-01-16T09:10:00Z',
  },
  {
    id: 'result-004',
    documentId: 'doc-004',
    documentName: 'madrid_protest_notes.txt',
    schemaId: 'schema-001',
    data: {
      protest_date: { value: '2023-04-22', confidence: 94 },
      city: { value: 'Madrid', confidence: 100 },
      country: { value: 'Spain', confidence: 100 },
      participant_count: { value: 5000, confidence: 68, sourceText: 'thousands of protesters' },
      protest_topic: { value: 'General environmental issues', confidence: 75 },
      violence_occurred: { value: 'No', confidence: 92 },
      police_response: { value: 'Observation only', confidence: 88 },
    },
    flagged: true,
    reviewNotes: 'Low confidence on participant count and protest topic',
    extractedAt: '2024-01-16T09:15:00Z',
  },
  {
    id: 'result-005',
    documentId: 'doc-005',
    documentName: 'amsterdam_climate_action.pdf',
    schemaId: 'schema-001',
    data: {
      protest_date: { value: '2023-05-15', confidence: 97 },
      city: { value: 'Amsterdam', confidence: 100 },
      country: { value: 'Netherlands', confidence: 100 },
      participant_count: { value: 12000, confidence: 86 },
      protest_topic: { value: 'Fossil fuels', confidence: 91, sourceText: 'opposing new oil drilling permits' },
      violence_occurred: { value: 'No', confidence: 96 },
      police_response: { value: 'None', confidence: 93, sourceText: 'no police presence required' },
    },
    flagged: false,
    extractedAt: '2024-01-16T09:20:00Z',
  },
];

// Generate additional mock results for larger dataset
for (let i = 6; i <= 100; i++) {
  const cities = ['Brussels', 'Copenhagen', 'Stockholm', 'Vienna', 'Rome', 'Barcelona', 'Prague', 'Warsaw'];
  const countries = ['Belgium', 'Denmark', 'Sweden', 'Austria', 'Italy', 'Spain', 'Czech Republic', 'Poland'];
  const topics = ['Climate policy', 'Fossil fuels', 'Deforestation', 'General environmental issues'];
  const policeResponses = ['None', 'Observation only', 'Crowd control', 'Arrests made'];

  const cityIndex = Math.floor(Math.random() * cities.length);
  const avgConfidence = 70 + Math.random() * 30; // 70-100

  mockExtractionResults.push({
    id: `result-${String(i).padStart(3, '0')}`,
    documentId: `doc-${String(i).padStart(3, '0')}`,
    documentName: `document_${i}.pdf`,
    schemaId: 'schema-001',
    data: {
      protest_date: {
        value: `2023-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
        confidence: randomConfidence(85, 100),
      },
      city: { value: cities[cityIndex], confidence: randomConfidence(95, 100) },
      country: { value: countries[cityIndex], confidence: randomConfidence(95, 100) },
      participant_count: { value: Math.floor(Math.random() * 20000) + 1000, confidence: randomConfidence(65, 95) },
      protest_topic: { value: topics[Math.floor(Math.random() * topics.length)], confidence: randomConfidence(75, 98) },
      violence_occurred: { value: Math.random() > 0.8 ? 'Yes' : 'No', confidence: randomConfidence(85, 98) },
      police_response: { value: policeResponses[Math.floor(Math.random() * policeResponses.length)], confidence: randomConfidence(80, 96) },
    },
    flagged: avgConfidence < 80,
    extractedAt: `2024-01-16T${String(9 + Math.floor(i / 10)).padStart(2, '0')}:${String((i * 5) % 60).padStart(2, '0')}:00Z`,
  });
}

/**
 * Get extraction results for a project
 */
export function getMockResultsByProjectId(projectId: string): ExtractionResult[] {
  // Return results for proj-001 (Climate Protests)
  if (projectId === 'proj-001') {
    return mockExtractionResults;
  }
  return [];
}

/**
 * Get extraction result by ID
 */
export function getMockResultById(id: string): ExtractionResult | undefined {
  return mockExtractionResults.find(r => r.id === id);
}

/**
 * Flag/unflag result (mock)
 */
export function toggleMockResultFlag(id: string): ExtractionResult | undefined {
  const result = mockExtractionResults.find(r => r.id === id);
  if (result) {
    result.flagged = !result.flagged;
  }
  return result;
}
