import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { TranscriptInput } from "./components/TranscriptInput";
import { TranscriptViewer } from "./components/TranscriptViewer";
import { EntityStatements } from "./components/EntityStatements";
import { scrollToSegment } from "./components/ReferenceHighlight";
import { extractEntities } from "./api/client";
import { TranscriptSegment, ExtractionResult } from "./types";

function App() {
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [highlightedSegments, setHighlightedSegments] = useState<Set<number>>(
    new Set()
  );

  const mutation = useMutation({
    mutationFn: extractEntities,
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleSubmit = useCallback(
    (newTranscript: TranscriptSegment[]) => {
      setTranscript(newTranscript);
      setResult(null);
      setHighlightedSegments(new Set());
      mutation.mutate({ transcript: newTranscript });
    },
    [mutation]
  );

  const handleHoverField = useCallback((segments: number[] | null) => {
    setHighlightedSegments(new Set(segments || []));
  }, []);

  const handleClickField = useCallback((segments: number[]) => {
    if (segments.length > 0) {
      scrollToSegment(segments[0]);
    }
  }, []);

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <header className="flex-shrink-0 bg-white shadow-sm border-b">
        <div className="max-w-full px-4 py-3">
          <h1 className="text-xl font-bold text-gray-900">
            Medicininių Entitetų Išgavimas
          </h1>
          <p className="text-xs text-gray-600">
            E025 Ambulatorinio apsilankymo aprašymas
          </p>
        </div>
      </header>

      {/* Error banner */}
      {mutation.error && (
        <div className="flex-shrink-0 mx-4 mt-2 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
          Klaida: {mutation.error.message}
        </div>
      )}

      {/* Main content - fixed height split panels */}
      <main className="flex-1 min-h-0 p-4">
        <div className="h-full grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Left panel - Input & Transcript */}
          <div className="h-full flex flex-col min-h-0 space-y-4">
            {/* Input section - collapsible when transcript loaded */}
            {transcript.length === 0 ? (
              <div className="flex-1 min-h-0">
                <TranscriptInput
                  onSubmit={handleSubmit}
                  isLoading={mutation.isPending}
                />
              </div>
            ) : (
              <>
                {/* Compact input toggle */}
                <div className="flex-shrink-0 bg-white rounded-lg shadow p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      Transkripcija įkelta ({transcript.length} segmentai)
                    </span>
                    <button
                      onClick={() => {
                        setTranscript([]);
                        setResult(null);
                      }}
                      className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
                    >
                      Nauja transkripcija
                    </button>
                  </div>
                </div>

                {/* Transcript viewer - scrollable */}
                <div className="flex-1 min-h-0 bg-white rounded-lg shadow overflow-hidden">
                  <div className="h-full overflow-y-auto p-4">
                    <h2 className="text-lg font-semibold mb-3 sticky top-0 bg-white pb-2 border-b">
                      Transkripcija
                    </h2>
                    <TranscriptViewer
                      transcript={transcript}
                      highlightedSegments={highlightedSegments}
                    />
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Right panel - Results */}
          <div className="h-full bg-white rounded-lg shadow overflow-hidden">
            <div className="h-full p-4">
              {result ? (
                <EntityStatements
                  document={result.document}
                  references={result.references}
                  onHoverField={handleHoverField}
                  onClickField={handleClickField}
                />
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-500">
                  <div className="text-center">
                    <h2 className="text-xl font-semibold mb-2">Išgauti Duomenys</h2>
                    <p className="italic">
                      {mutation.isPending
                        ? "Analizuojama transkripcija..."
                        : "Įkelkite transkripciją ir spauskite 'Išgauti Entitetus'"}
                    </p>
                    {mutation.isPending && (
                      <div className="mt-4 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
