import React from "react";
import { AbsoluteFill, Audio } from "remotion";
import { KenBurnsImage } from "../components/KenBurnsImage";
import { SubtitulosWhisper, WordTimestamp } from "../SubtitulosWhisper";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface SplitKaraokeProps {
  topImageSrc?: string;
  topTitle?: string;
  presenterVideoSrc?: string;
  audioSrc?: string;
  words?: WordTimestamp[];
  projectSlug?: string;
}

export const SplitKaraokeTemplate: React.FC<SplitKaraokeProps> = ({
  topImageSrc,
  topTitle = "ANÁLISIS DE ARQUITECTURA",
  presenterVideoSrc,
  audioSrc,
  words,
  projectSlug,
}) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B0F19",
        color: "#F8FAFC",
        fontFamily: "'Inter', sans-serif",
        display: "flex",
        flexDirection: "column",
        padding: "36px 40px 48px 40px",
        boxSizing: "border-box",
        overflow: "hidden",
      }}
    >
      <ReadingProgressBar color="#38BDF8" height={8} />
      {audioSrc && <Audio src={audioSrc} />}

      {/* 1. SECCIÓN SUPERIOR (55%): Contenido visual / Ken Burns */}
      <div
        style={{
          height: "55%",
          width: "100%",
          position: "relative",
          borderRadius: 28,
          overflow: "hidden",
          border: "2px solid rgba(56, 189, 248, 0.25)",
          boxShadow: "0 20px 40px rgba(0, 0, 0, 0.6)",
        }}
      >
        <KenBurnsImage src={topImageSrc} zoomDirection="in" maxScale={1.12} borderRadius={26} />

        {/* Titular superior flotante */}
        <div
          style={{
            position: "absolute",
            top: 24,
            left: 24,
            padding: "8px 18px",
            borderRadius: 999,
            backgroundColor: "rgba(11, 15, 25, 0.85)",
            backdropFilter: "blur(10px)",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            color: "#38BDF8",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 18,
            fontWeight: 700,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          {topTitle}
        </div>
      </div>

      {/* 2. SECCIÓN CENTRAL (15%): Franja Karaoke */}
      <div
        style={{
          height: "15%",
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        <SubtitulosWhisper words={words} projectSlug={projectSlug} chunkSize={3} />
      </div>

      {/* 3. SECCIÓN INFERIOR (30%): Cámara del Presentador en zona segura */}
      <div
        style={{
          height: "30%",
          width: "100%",
          borderRadius: 28,
          overflow: "hidden",
          backgroundColor: "#111827",
          border: "2px solid rgba(255, 255, 255, 0.12)",
          boxShadow: "0 16px 36px rgba(0, 0, 0, 0.5)",
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {presenterVideoSrc ? (
          <video
            src={presenterVideoSrc}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              textAlign: "center",
              color: "#94A3B8",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            <div style={{ fontSize: 22, color: "#10B981", marginBottom: 6 }}>
              ● CÁMARA PRESENTADOR
            </div>
            <div style={{ fontSize: 16 }}>Zona Segura Vertical</div>
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
