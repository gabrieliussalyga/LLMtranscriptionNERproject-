// Export all generated types from the backend schema
export * from './generated';

import { ExtractionResult } from './generated';

// Transcript types (Input)
export interface TranscriptSegment {
  time: string;
  speaker: string;
  text: string;
}

export interface TranscriptInput {
  meta?: Record<string, unknown>;
  transcript: TranscriptSegment[];
}

// App state types
export interface AppState {
  transcript: TranscriptSegment[];
  result: ExtractionResult | null;
  isLoading: boolean;
  error: string | null;
  highlightedSegments: Set<number>;
  selectedField: string | null;
}