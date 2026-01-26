import { TranscriptSegment } from "../types";

interface TranscriptViewerProps {
  transcript: TranscriptSegment[];
  highlightedSegments: Set<number>;
}

export function TranscriptViewer({
  transcript,
  highlightedSegments,
}: TranscriptViewerProps) {
  if (transcript.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Transkripcija</h2>
        <p className="text-gray-500 italic">
          Įkelkite transkripciją kairėje pusėje
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Transkripcija</h2>
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {transcript.map((segment, index) => (
          <div
            key={index}
            id={`segment-${index}`}
            className={`p-3 rounded transition-colors ${
              highlightedSegments.has(index)
                ? "bg-yellow-100 border-l-4 border-yellow-500"
                : "bg-gray-50"
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-gray-400 font-mono">
                [{segment.time}]
              </span>
              <span
                className={`text-sm font-medium ${
                  segment.speaker === "Gydytojas"
                    ? "text-blue-600"
                    : "text-green-600"
                }`}
              >
                {segment.speaker}:
              </span>
            </div>
            <p className="text-gray-800">{segment.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
