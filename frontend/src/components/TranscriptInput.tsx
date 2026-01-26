import { useState } from "react";
import { TranscriptSegment } from "../types";

interface TranscriptInputProps {
  onSubmit: (transcript: TranscriptSegment[]) => void;
  isLoading: boolean;
}

const SAMPLE_TRANSCRIPT = `{
  "transcript": [
    {"time": "00:00:01", "speaker": "Gydytojas", "text": "Laba diena, prašom sėstis. Kas jus atveda?"},
    {"time": "00:00:05", "speaker": "Pacientas", "text": "Laba diena. Atėjau pasitikrinti, nes jau keletą dienų jaučiu silpnumą."},
    {"time": "00:00:12", "speaker": "Gydytojas", "text": "Ar turite kokių nors alergijų?"},
    {"time": "00:00:15", "speaker": "Pacientas", "text": "Taip, esu alergiškas beržui ir kai kuriems maisto produktams - šokoladui, citrusams, braškėms ir obuoliams."},
    {"time": "00:00:25", "speaker": "Gydytojas", "text": "Supratau. O kokios jūsų lėtinės ligos?"},
    {"time": "00:00:30", "speaker": "Pacientas", "text": "Turiu problemų su skydliauke, padidėjęs cholesterolis, psoriazė ir refliuksas."},
    {"time": "00:00:40", "speaker": "Gydytojas", "text": "Išmatuosiu jūsų gyvybinius rodiklius. Temperatūra 36.6, kraujospūdis 115 per 83, pulsas 69, saturacija 97 procentai."},
    {"time": "00:00:55", "speaker": "Gydytojas", "text": "Viskas atrodo gerai. Rekomenduoju daugiau ilsėtis ir gerti skysčių."}
  ]
}`;

export function TranscriptInput({ onSubmit, isLoading }: TranscriptInputProps) {
  const [inputText, setInputText] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = () => {
    setError(null);
    try {
      const parsed = JSON.parse(inputText);
      const transcript = parsed.transcript || parsed;

      if (!Array.isArray(transcript)) {
        throw new Error("Transcript must be an array");
      }

      for (const segment of transcript) {
        if (!segment.time || !segment.speaker || !segment.text) {
          throw new Error("Each segment must have time, speaker, and text");
        }
      }

      onSubmit(transcript);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid JSON");
    }
  };

  const handleLoadSample = () => {
    setInputText(SAMPLE_TRANSCRIPT);
    setError(null);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setInputText(content);
      setError(null);
    };
    reader.onerror = () => {
      setError("Failed to read file");
    };
    reader.readAsText(file);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Transkripcijos Įvestis</h2>

      <div className="mb-4 flex gap-2">
        <button
          onClick={handleLoadSample}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded text-sm"
        >
          Įkelti pavyzdį
        </button>
        <label className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded text-sm cursor-pointer">
          Įkelti failą
          <input
            type="file"
            accept=".json"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </div>

      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="Įklijuokite JSON transkripciją..."
        className="w-full h-64 p-3 border border-gray-300 rounded font-mono text-sm resize-y focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />

      {error && (
        <div className="mt-2 text-red-600 text-sm">{error}</div>
      )}

      <button
        onClick={handleSubmit}
        disabled={isLoading || !inputText.trim()}
        className="mt-4 w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded transition-colors"
      >
        {isLoading ? "Analizuojama..." : "Išgauti Entitetus"}
      </button>
    </div>
  );
}
