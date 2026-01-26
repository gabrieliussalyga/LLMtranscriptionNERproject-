import { useEffect } from "react";

interface ReferenceHighlightProps {
  segments: number[];
}

export function ReferenceHighlight({ segments }: ReferenceHighlightProps) {
  useEffect(() => {
    if (segments.length === 0) return;

    const firstSegment = document.getElementById(`segment-${segments[0]}`);
    if (firstSegment) {
      firstSegment.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [segments]);

  return null;
}

export function scrollToSegment(segmentIndex: number): void {
  const element = document.getElementById(`segment-${segmentIndex}`);
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}
