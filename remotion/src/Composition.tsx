import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { SubtitulosWhisper, WordTimestamp } from "./SubtitulosWhisper";
import { BackdropInsert } from "./BackdropInsert";
import { DynamicZoom } from "./DynamicZoom";

export interface MainCompositionProps {
  title?: string;
  subtitle?: string;
  projectSlug?: string;
  audioSrc?: string;
  words?: WordTimestamp[];
}

export const MainComposition: React.FC<MainCompositionProps> = ({
  title = "VideoFactory Studio",
  subtitle = "Arquitectura de Software y Agentes IA",
  projectSlug = "demo_test",
  audioSrc,
  words,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animación de entrada fluida para el título
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleScale = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B0F19",
        color: "#F8FAFC",
        fontFamily: "'Inter', sans-serif",
        overflow: "hidden",
      }}
    >
      {audioSrc && <Audio src={audioSrc} />}

      <DynamicZoom
        zoomPoints={[
          { startFrame: 0, scale: 1.0 },
          { startFrame: 35, scale: 1.05, originY: "40%" },
          { startFrame: 90, scale: 1.0 },
        ]}
      >
        {/* Fondo decorativo con gradiente tecnológico sutil */}
        <AbsoluteFill
          style={{
            background:
              "radial-gradient(circle at 50% 30%, rgba(56, 189, 248, 0.12) 0%, transparent 70%), radial-gradient(circle at 80% 80%, rgba(16, 185, 129, 0.08) 0%, transparent 60%)",
          }}
        />

        {/* BackdropInsert demo en tercio superior */}
        <BackdropInsert
          type="image"
          mode="vertical-top"
          startFrame={20}
          durationFrames={100}
          title="ARQUITECTURA // PIPELINE"
          subtitle="Automatización de Video con IA"
        />

        {/* Cabecera Principal */}
        <div
          style={{
            position: "absolute",
            top: 220,
            left: 60,
            right: 60,
            textAlign: "center",
            opacity: titleOpacity,
            transform: `scale(${titleScale})`,
          }}
        >
          <div
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 28,
              letterSpacing: "0.2em",
              color: "#38BDF8",
              textTransform: "uppercase",
              marginBottom: 16,
            }}
          >
            VideoFactory
          </div>
          <h1
            style={{
              fontSize: 64,
              fontWeight: 800,
              lineHeight: 1.15,
              margin: 0,
              letterSpacing: "-0.02em",
              background: "linear-gradient(180deg, #FFFFFF 0%, #94A3B8 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            {title}
          </h1>
          {subtitle && (
            <p
              style={{
                fontSize: 32,
                color: "#94A3B8",
                marginTop: 20,
                lineHeight: 1.4,
              }}
            >
              {subtitle}
            </p>
          )}
        </div>

        {/* Subtítulos cinéticos dinámicos sincronizados con Whisper */}
        <SubtitulosWhisper words={words} projectSlug={projectSlug} />
      </DynamicZoom>
    </AbsoluteFill>
  );
};
