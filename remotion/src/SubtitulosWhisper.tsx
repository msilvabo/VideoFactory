import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

export interface WordTimestamp {
  word: string;
  start: number;
  end: number;
}

export interface SubtitulosWhisperProps {
  words?: WordTimestamp[];
  projectSlug?: string;
  chunkSize?: number;
}

export const SubtitulosWhisper: React.FC<SubtitulosWhisperProps> = ({
  words: wordsProp,
  projectSlug,
  chunkSize = 3,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Si no se pasaron palabras como prop, intentar cargar desde memoria o mostrar demo
  const allWords = wordsProp && wordsProp.length > 0 ? wordsProp : [
    { word: "VideoFactory", start: 0.2, end: 0.9 },
    { word: "ha", start: 0.95, end: 1.2 },
    { word: "sido", start: 1.25, end: 1.6 },
    { word: "configurado", start: 1.65, end: 2.3 },
    { word: "correctamente", start: 2.35, end: 3.2 },
    { word: "y", start: 3.25, end: 3.4 },
    { word: "listo", start: 3.45, end: 3.9 },
    { word: "para", start: 3.95, end: 4.2 },
    { word: "producción", start: 4.25, end: 4.8 },
  ];

  // Agrupar en fragmentos (chunks)
  const chunks: WordTimestamp[][] = [];
  for (let i = 0; i < allWords.length; i += chunkSize) {
    chunks.push(allWords.slice(i, i + chunkSize));
  }

  // Encontrar el chunk activo
  const activeChunk = chunks.find((chunk) => {
    const chunkStart = chunk[0].start;
    const chunkEnd = chunk[chunk.length - 1].end;
    return currentTime >= chunkStart && currentTime <= chunkEnd + 0.35;
  });

  if (!activeChunk) {
    return null;
  }

  return (
    <div
      style={{
        position: "absolute",
        bottom: 340, // Dejando libre la zona inferior de TikTok/Reels/Shorts
        left: 48,
        right: 48,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        alignItems: "center",
        gap: "14px 20px",
        zIndex: 100,
        pointerEvents: "none",
      }}
    >
      {activeChunk.map((item, index) => {
        const isCurrentWord =
          currentTime >= item.start && currentTime <= item.end;
        return (
          <span
            key={`${item.word}-${index}`}
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 56,
              fontWeight: 900,
              letterSpacing: "-0.01em",
              color: isCurrentWord ? "#38BDF8" : "#FFFFFF",
              transform: isCurrentWord ? "scale(1.10)" : "scale(1.0)",
              transition: "transform 0.08s ease-out, color 0.08s ease-out",
              textShadow:
                "0 4px 16px rgba(0,0,0,0.9), 0 2px 4px rgba(0,0,0,0.8)",
              display: "inline-block",
            }}
          >
            {item.word}
          </span>
        );
      })}
    </div>
  );
};
