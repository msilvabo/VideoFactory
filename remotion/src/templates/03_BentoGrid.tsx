import React from "react";
import { AbsoluteFill, Audio } from "remotion";
import { BentoCard, BentoCardProps } from "../components/BentoCard";
import { SubtitulosWhisper, WordTimestamp } from "../SubtitulosWhisper";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface BentoGridProps {
  headerTitle?: string;
  cards?: BentoCardProps[];
  presenterVideoSrc?: string;
  audioSrc?: string;
  words?: WordTimestamp[];
}

export const BentoGridTemplate: React.FC<BentoGridProps> = ({
  headerTitle = "3 PILARES DE ARQUITECTURA",
  cards = [
    {
      title: "Desacoplamiento Modular",
      subtitle: "Componentes aislados independientes de infraestructura",
      badge: "PILARES #1",
      value: "100%",
      color: "#38BDF8",
      delayFrames: 10,
    },
    {
      title: "Test-Driven Dev",
      subtitle: "Verificación antes de escribir código",
      badge: "CALIDAD #2",
      value: "98.4%",
      color: "#10B981",
      delayFrames: 30,
    },
    {
      title: "Agentes Autónomos",
      subtitle: "Orquestación de pipelines con LLMs",
      badge: "VELOCIDAD #3",
      value: "10X",
      color: "#F59E0B",
      delayFrames: 50,
    },
  ],
  presenterVideoSrc,
  audioSrc,
  words,
}) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B0F19",
        color: "#F8FAFC",
        fontFamily: "'Inter', sans-serif",
        padding: "36px 40px 48px 40px",
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      <ReadingProgressBar color="#10B981" />
      {audioSrc && <Audio src={audioSrc} />}

      {/* Titular superior */}
      <div style={{ marginTop: 20, marginBottom: 20, textAlign: "center" }}>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 20,
            color: "#38BDF8",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
          }}
        >
          {headerTitle}
        </span>
      </div>

      {/* Zona Superior (65%): Cuadrícula Bento 3X */}
      <div
        style={{
          height: "60%",
          display: "flex",
          flexDirection: "column",
          gap: 18,
        }}
      >
        {/* Tarjeta 1 Panorámica (Full Width) */}
        {cards[0] && (
          <div style={{ flex: 1.1 }}>
            <BentoCard {...cards[0]} style={{ height: "100%" }} />
          </div>
        )}

        {/* Tarjetas 2 y 3 (Columnas 50% - 50%) */}
        <div style={{ flex: 1, display: "flex", gap: 18 }}>
          {cards[1] && (
            <div style={{ flex: 1 }}>
              <BentoCard {...cards[1]} style={{ height: "100%" }} />
            </div>
          )}
          {cards[2] && (
            <div style={{ flex: 1 }}>
              <BentoCard {...cards[2]} style={{ height: "100%" }} />
            </div>
          )}
        </div>
      </div>

      {/* Zona Inferior (35%): Presentador + Subtítulos */}
      <div
        style={{
          marginTop: 24,
          height: "32%",
          borderRadius: 28,
          backgroundColor: "#111827",
          border: "2px solid rgba(255, 255, 255, 0.1)",
          position: "relative",
          overflow: "hidden",
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
              fontFamily: "'JetBrains Mono', monospace",
              color: "#64748B",
              fontSize: 20,
            }}
          >
            [ CÁMARA PRESENTADOR / B-ROLL ]
          </div>
        )}
        <SubtitulosWhisper words={words} />
      </div>
    </AbsoluteFill>
  );
};
