import React from "react";
import { AbsoluteFill, Audio, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { HighlighterStroke } from "../components/HighlighterStroke";
import { SubtitulosWhisper, WordTimestamp } from "../SubtitulosWhisper";
import { PipCapsule } from "../components/PipCapsule";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface VoxHighlighterProps {
  publicationName?: string;
  articleDate?: string;
  preText?: string;
  highlightedText?: string;
  postText?: string;
  highlightColor?: string;
  highlightStartFrame?: number;
  highlightDuration?: number;
  webcamSrc?: string;
  audioSrc?: string;
  words?: WordTimestamp[];
}

export const VoxHighlighterTemplate: React.FC<VoxHighlighterProps> = ({
  publicationName = "THE ARCHITECTURE REVIEW",
  articleDate = "NOVIEMBRE 2026",
  preText = "Los benchmarks confirman que ",
  highlightedText = "la automatización con agentes de IA reduce errores en un 84%",
  postText = " comparado con procesos de refactorización tradicionales.",
  highlightColor = "#FACC15",
  highlightStartFrame = 25,
  highlightDuration = 35,
  webcamSrc,
  audioSrc,
  words,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardEnter = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.7 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0F172A",
        overflow: "hidden",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <ReadingProgressBar color="#FACC15" />
      {audioSrc && <Audio src={audioSrc} />}

      {/* Fondo con textura tecnológica sutil y cuadrícula */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 30%, #1E293B 0%, #0B0F19 100%)",
          backgroundImage:
            "radial-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      {/* Tarjeta de artículo estilo VOX con inclinación 3D sutil */}
      <div
        style={{
          position: "absolute",
          top: 260,
          left: 50,
          right: 50,
          backgroundColor: "#FFFFFF",
          color: "#0F172A",
          borderRadius: 24,
          padding: "44px 40px",
          boxShadow:
            "0 30px 60px rgba(0, 0, 0, 0.7), 0 10px 20px rgba(0, 0, 0, 0.4)",
          transform: `scale(${cardEnter}) rotateZ(-1.2deg)`,
          transformOrigin: "center center",
          zIndex: 50,
        }}
      >
        {/* Cabecera del artículo */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            borderBottom: "2px solid #E2E8F0",
            paddingBottom: 16,
            marginBottom: 24,
          }}
        >
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 16,
              fontWeight: 800,
              color: "#64748B",
              letterSpacing: "0.1em",
            }}
          >
            {publicationName}
          </span>
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 14,
              color: "#94A3B8",
            }}
          >
            {articleDate}
          </span>
        </div>

        {/* Texto con subrayador Vox animado */}
        <div
          style={{
            fontSize: 34,
            fontWeight: 700,
            lineHeight: 1.45,
            color: "#0F172A",
            letterSpacing: "-0.01em",
          }}
        >
          {preText}
          <HighlighterStroke
            startFrame={highlightStartFrame}
            durationFrames={highlightDuration}
            color={highlightColor}
            heightPercent={55}
          >
            <span style={{ color: "#000000", fontWeight: 800 }}>
              {highlightedText}
            </span>
          </HighlighterStroke>
          {postText}
        </div>
      </div>

      {/* Mini Cápsula del narrador */}
      <PipCapsule src={webcamSrc} bottom={320} right={48} width={220} height={280} />

      {/* Subtítulos */}
      <SubtitulosWhisper words={words} />
    </AbsoluteFill>
  );
};
