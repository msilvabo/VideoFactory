import React from "react";
import { AbsoluteFill, Audio, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { AudioWaveform } from "../components/AudioWaveform";
import { SubtitulosWhisper, WordTimestamp } from "../SubtitulosWhisper";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface NewsCardWaveformProps {
  presenterVideoSrc?: string;
  sourceBadge?: string;
  headline?: string;
  quote?: string;
  popStartFrame?: number;
  popDuration?: number;
  audioSrc?: string;
  words?: WordTimestamp[];
  waveformValues?: number[];
}

export const NewsCardWaveformTemplate: React.FC<NewsCardWaveformProps> = ({
  presenterVideoSrc,
  sourceBadge = "WIRED // EXCLUSIVA",
  headline = "La Arquitectura de Agentes Multi-Modelo Supera el Código Manual",
  quote = "«El 82% de las empresas de software de alto crecimiento ahora integran validación automatizada por agentes antes del despliegue.»",
  popStartFrame = 20,
  popDuration = 90,
  audioSrc,
  words,
  waveformValues,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isPopActive = frame >= popStartFrame && frame <= popStartFrame + popDuration;
  const localFrame = Math.max(0, frame - popStartFrame);

  const popProgress = spring({
    frame: isPopActive ? localFrame : 0,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  const dimBg = interpolate(popProgress, [0, 1], [1.0, 0.55]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B0F19",
        overflow: "hidden",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <ReadingProgressBar color="#F59E0B" />
      {audioSrc && <Audio src={audioSrc} />}

      {/* 1. Fondo: Video del presentador con oscurecimiento suave */}
      <AbsoluteFill
        style={{
          filter: `brightness(${dimBg})`,
          transition: "filter 0.1s ease-out",
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
              width: "100%",
              height: "100%",
              background: "linear-gradient(180deg, #1E293B 0%, #0F172A 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#64748B",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 24,
            }}
          >
            [ CÁMARA PRESENTADOR ]
          </div>
        )}
      </AbsoluteFill>

      {/* 2. Tarjeta Pop-Up Flotante Central */}
      {popProgress > 0.05 && (
        <div
          style={{
            position: "absolute",
            top: 280,
            left: 50,
            right: 50,
            padding: "36px 36px 28px 36px",
            borderRadius: 32,
            backgroundColor: "rgba(15, 23, 42, 0.92)",
            border: "2px solid rgba(245, 158, 11, 0.4)",
            boxShadow:
              "0 30px 60px rgba(0, 0, 0, 0.8), 0 0 35px rgba(245, 158, 11, 0.2)",
            backdropFilter: "blur(18px)",
            transform: `scale(${popProgress}) translateY(${(1 - popProgress) * 50}px)`,
            zIndex: 60,
          }}
        >
          {/* Badge de fuente */}
          <div
            style={{
              display: "inline-block",
              padding: "6px 16px",
              borderRadius: 999,
              backgroundColor: "rgba(245, 158, 11, 0.2)",
              border: "1px solid #F59E0B",
              color: "#F59E0B",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 16,
              fontWeight: 800,
              letterSpacing: "0.1em",
              marginBottom: 16,
            }}
          >
            {sourceBadge}
          </div>

          {/* Titular */}
          <h2
            style={{
              margin: "0 0 16px 0",
              fontSize: 38,
              fontWeight: 800,
              lineHeight: 1.2,
              color: "#FFFFFF",
              letterSpacing: "-0.02em",
            }}
          >
            {headline}
          </h2>

          {/* Cita */}
          <p
            style={{
              margin: "0 0 24px 0",
              fontSize: 22,
              lineHeight: 1.45,
              color: "#CBD5E1",
              fontStyle: "italic",
            }}
          >
            {quote}
          </p>

          {/* Visualizador de onda de voz integrado */}
          <div
            style={{
              paddingTop: 16,
              borderTop: "1px solid rgba(255, 255, 255, 0.1)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 14,
                color: "#94A3B8",
                marginBottom: 8,
              }}
            >
              EN DIRECTO // FORMA DE ONDA
            </div>
            <AudioWaveform
              barCount={36}
              height={48}
              activeColor="#F59E0B"
              baseColor="rgba(245, 158, 11, 0.25)"
              waveformValues={waveformValues}
            />
          </div>
        </div>
      )}

      {/* 3. Subtítulos */}
      <SubtitulosWhisper words={words} />
    </AbsoluteFill>
  );
};
