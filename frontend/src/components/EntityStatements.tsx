import { useState } from "react";
import { E025Document, EntityReference } from "../types";

interface EntityStatementsProps {
  document: E025Document;
  references: EntityReference[];
  onHoverField: (segments: number[] | null) => void;
  onClickField: (segments: number[]) => void;
}

interface StatementRowProps {
  text: string;
  segments: number[];
  onHover: (segments: number[] | null) => void;
  onClick: (segments: number[]) => void;
  className?: string;
}

function StatementRow({ text, segments, onHover, onClick, className = "" }: StatementRowProps) {
  return (
    <div
      className={`p-2 rounded border cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-colors text-sm ${className}`}
      onMouseEnter={() => onHover(segments)}
      onMouseLeave={() => onHover(null)}
      onClick={() => segments.length > 0 && onClick(segments)}
    >
      <div className="flex justify-between items-start gap-2">
        <p className="text-gray-900 flex-1">{text}</p>
        {segments.length > 0 && (
          <span className="text-xs text-gray-400 whitespace-nowrap">
            [{segments.join(", ")}]
          </span>
        )}
      </div>
    </div>
  );
}

interface CollapsibleSectionProps {
  title: string;
  count: number;
  color: string;
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function CollapsibleSection({ title, count, color, isOpen, onToggle, children }: CollapsibleSectionProps) {
  return (
    <div className={`border rounded-lg overflow-hidden ${color}`}>
      <button
        onClick={onToggle}
        className="w-full px-3 py-2 flex items-center justify-between text-left font-medium text-sm hover:bg-black/5 transition-colors"
      >
        <span>{title} ({count})</span>
        <span className="text-lg">{isOpen ? "−" : "+"}</span>
      </button>
      {isOpen && (
        <div className="px-2 pb-2 space-y-1 max-h-48 overflow-y-auto">
          {children}
        </div>
      )}
    </div>
  );
}

type SectionKey =
  | "vital_signs"
  | "allergies"
  | "diagnosis"
  | "anamnesis"
  | "objective"
  | "tests_plan"
  | "tests_done"
  | "treatment"
  | "discharge"
  | "notes";

const SECTION_CONFIG: Record<SectionKey, { label: string; color: string }> = {
  vital_signs: { label: "Gyvybiniai Rodikliai", color: "bg-blue-50 border-blue-200" },
  allergies: { label: "Alergijos", color: "bg-red-50 border-red-200" },
  diagnosis: { label: "Diagnozė", color: "bg-purple-50 border-purple-200" },
  anamnesis: { label: "Anamnezė", color: "bg-gray-50 border-gray-300" },
  objective: { label: "Objektyvus Įvertinimas", color: "bg-teal-50 border-teal-200" },
  tests_plan: { label: "Planuojami Tyrimai", color: "bg-yellow-50 border-yellow-200" },
  tests_done: { label: "Atlikti Tyrimai", color: "bg-orange-50 border-orange-200" },
  treatment: { label: "Gydymas", color: "bg-green-50 border-green-200" },
  discharge: { label: "Būklė Išrašant", color: "bg-indigo-50 border-indigo-200" },
  notes: { label: "Pastabos", color: "bg-gray-50 border-gray-200" },
};

export function EntityStatements({
  document,
  onHoverField,
  onClickField,
}: EntityStatementsProps) {
  const [openSections, setOpenSections] = useState<Set<SectionKey>>(new Set(Object.keys(SECTION_CONFIG) as SectionKey[]));
  const [filter, setFilter] = useState<SectionKey | "all">("all");

  const toggleSection = (key: SectionKey) => {
    setOpenSections(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const expandAll = () => setOpenSections(new Set(Object.keys(SECTION_CONFIG) as SectionKey[]));
  const collapseAll = () => setOpenSections(new Set());

  // Get section data
  const sections: Record<SectionKey, { items: Array<{ text: string; segments: number[] }> }> = {
    vital_signs: {
      items: document.vital_signs?.items?.map(item => ({
        text: `${item.name}: ${item.value}`,
        segments: item.source_segments,
      })) || [],
    },
    allergies: {
      items: document.allergies?.map(a => {
        const typeLabels: Record<string, string> = { vaistai: "Vaistams", maistas: "Maistui", kita: "Kita" };
        return { text: `${typeLabels[a.type]}: ${a.description}`, segments: a.source_segments || [] };
      }) || [],
    },
    diagnosis: {
      items: document.diagnosis?.items?.map(item => {
        const certaintyLabels: Record<string, string> = { "+": "✓", "-": "✗", "0": "?" };
        const certainty = item.diagnosis_certainty ? ` (${certaintyLabels[item.diagnosis_certainty]})` : "";
        const code = item.diagnosis_code ? ` [${item.diagnosis_code}]` : "";
        return { text: `${item.diagnosis}${code}${certainty}`, segments: item.source_segments };
      }) || [],
    },
    anamnesis: {
      items: document.clinical_notes?.complaints_anamnesis?.map(item => ({
        text: item.statement,
        segments: item.source_segments,
      })) || [],
    },
    objective: {
      items: document.clinical_notes?.objective_condition?.map(item => ({
        text: item.statement,
        segments: item.source_segments,
      })) || [],
    },
    tests_plan: {
      items: document.clinical_notes?.tests_consultations_plan?.map(item => ({
        text: item.statement,
        segments: item.source_segments,
      })) || [],
    },
    tests_done: {
      items: document.clinical_notes?.performed_tests_consultations?.map(item => ({
        text: item.statement,
        segments: item.source_segments,
      })) || [],
    },
    treatment: {
      items: document.treatment?.items?.map(item => {
        const typeLabels: Record<string, string> = {
          medication: "💊", non_medication: "🏥", prescription: "📋",
          referral: "📤", recommendation: "💡", test: "🔬",
        };
        return { text: `${typeLabels[item.type] || ""} ${item.description}`, segments: item.source_segments };
      }) || [],
    },
    discharge: {
      items: document.clinical_notes?.condition_on_discharge?.map(item => ({
        text: item.statement,
        segments: item.source_segments,
      })) || [],
    },
    notes: {
      items: document.clinical_notes?.notes?.map(item => ({
        text: item.statement,
        segments: item.source_segments,
      })) || [],
    },
  };

  const availableSections = (Object.keys(sections) as SectionKey[]).filter(
    key => sections[key].items.length > 0
  );

  const visibleSections = filter === "all"
    ? availableSections
    : availableSections.filter(key => key === filter);

  const totalItems = availableSections.reduce((sum, key) => sum + sections[key].items.length, 0);

  if (totalItems === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 italic">
        Nepavyko išgauti jokių duomenų iš transkripcijos.
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header with controls */}
      <div className="flex-shrink-0 pb-3 border-b mb-3 space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Išgauti Duomenys ({totalItems})</h2>
          <div className="flex gap-1">
            <button
              onClick={expandAll}
              className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
            >
              Išskleisti
            </button>
            <button
              onClick={collapseAll}
              className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
            >
              Sutraukti
            </button>
          </div>
        </div>

        {/* Filter dropdown */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value as SectionKey | "all")}
          className="w-full p-2 text-sm border rounded bg-white"
        >
          <option value="all">Visos kategorijos ({availableSections.length})</option>
          {availableSections.map(key => (
            <option key={key} value={key}>
              {SECTION_CONFIG[key].label} ({sections[key].items.length})
            </option>
          ))}
        </select>
      </div>

      {/* Scrollable sections */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {visibleSections.map(key => (
          <CollapsibleSection
            key={key}
            title={SECTION_CONFIG[key].label}
            count={sections[key].items.length}
            color={SECTION_CONFIG[key].color}
            isOpen={openSections.has(key)}
            onToggle={() => toggleSection(key)}
          >
            {sections[key].items.map((item, index) => (
              <StatementRow
                key={index}
                text={item.text}
                segments={item.segments}
                onHover={onHoverField}
                onClick={onClickField}
                className="bg-white/50"
              />
            ))}
          </CollapsibleSection>
        ))}
      </div>
    </div>
  );
}
