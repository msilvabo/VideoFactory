import React from "react";
import { AbsoluteFill, Audio, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { ReadingProgressBar } from "../components/ReadingProgressBar";
import { SubtitulosWhisper, WordTimestamp } from "../SubtitulosWhisper";

export interface SmartReframeProps {
  videoHorizontalSrc?: string;
  headerHeadline?: string;
  headerSub?: string;
  panCurveX?: number[]; // Valores de 0 a 100 indicando posición de encuadre horizontal
  audioSrc?: string;
  words?: WordTimestamp[];
}

export const SmartReframeTemplate: React.FC<SmartReframeProps> = ({
  videoHorizontalSrc,
  headerHeadline = "LO QUE NO TE CONTARON",
  headerSub = "Arquitectura de Software y Agentes Autónomos",
  panCurveX,
  audioSrc,
  words,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Paneo horizontal calculado por curva o interpolación oscilante suave
  let currentPanX = 50;
  if (panCurveX && panCurveX.length > 0) {
    const idx = Math.min(frame, panCurveX.length - 1);
    currentPanX = panCurveX[idx];
  } else {
    currentPanX = interpolate(
      frame,
      [0, durationInFrames / 2, durationInFrames],
      [45, 55, 45],
      { extrapolateRight: "clamp" }
    );
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B0F19",
        overflow: "hidden",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <ReadingProgressBar color="#38BDF8" height={10} />
      {audioSrc && <Audio src={audioSrc} />}

      {/* 1. Capa Base (100%): Video 16:9 ampliado con fuerte desenfoque */}
      <AbsoluteFill
        style={{
          filter: "blur(30px) brightness(0.45)",
          transform: "scale(1.2)",
        }}
      >
        {videoHorizontalSrc ? (
          <video
            src={videoHorizontalSrc}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background: "linear-gradient(135deg, #1E293B 0%, #0F172A 100%)",
            }}
          />
        )}
      </AbsoluteFill>

      {/* 2. Titular superior fijo de alto impacto */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 48,
          right: 48,
          textAlign: "center",
          zIndex: 50,
        }}
      >
        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 22,
            color: "#FACC15",
            fontWeight: 800,
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: 8,
          }}
        >
          {headerHeadline}
        </div>
        <div
          style={{
            fontSize: 32,
            fontWeight: 800,
            color: "#FFFFFF",
            lineHeight: 1.25,
            letterSpacing: "-0.01em",
          }}
        >
          {headerSub}
        </div>
      </div>

      {/* 3. Capa Central (55% de altura): Video horizontal re-encuadrado con seguimiento */}
      <div
        style={{
          position: "absolute",
          top: "28%",
          left: 36,
          right: 36,
          height: "46%",
          borderRadius: 32,
          overflow: "hidden",
          border: "2px solid rgba(56, 189, 248, 0.4)",
          boxShadow:
            "0 30px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(56, 189, 248, 0.25)",
          zIndex: 40,
          backgroundColor: "#0F172A",
        }}
      >
        {videoHorizontalSrc ? (
          <video
            src={videoHorizontalSrc}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: `${currentPanX}% center`,
              transition: "object-position 0.1s linear",
            }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "#38BDF8",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            <div style={{ fontSize: 24, fontWeight: 700 }}>
              AUTO-PANNING TRACKER
            </div>
            <div style={{ fontSize: 16, color: "#94A3B8", marginTop: 8 }}>
              Offset X: {currentPanX.toFixed(1)}%
            </div>
          </div>
        )}
      </div>

      {/* 4. Subtítulos dinámicos inferiores */}
      <SubtitulosWhisper words={words} />
    </AbsoluteFill>
  );
};
