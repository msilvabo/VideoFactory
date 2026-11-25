import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SubtitulosWhisper, WordTimestamp } from "../SubtitulosWhisper";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface BeforeAfterProps {
  beforeImgSrc?: string;
  afterImgSrc?: string;
  beforeLabel?: string;
  afterLabel?: string;
  dividerStartFrame?: number;
  dividerDuration?: number;
  audioSrc?: string;
  words?: WordTimestamp[];
}

export const BeforeAfterTemplate: React.FC<BeforeAfterProps> = ({
  beforeImgSrc,
  afterImgSrc,
  beforeLabel = "ANTES // MITO",
  afterLabel = "DESPUÉS // REALIDAD",
  dividerStartFrame = 25,
  dividerDuration = 70,
  audioSrc,
  words,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - dividerStartFrame);
  const wipeProgress = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 15, mass: 0.8 },
  });

  // Porcentaje de revelación de 0 a 100
  const cutPercent = interpolate(wipeProgress, [0, 1], [0, 100], {
    extrapolateRight: "clamp",
  });

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

      {/* Capa 1: ESCENARIO A (Antes) */}
      <AbsoluteFill>
        {beforeImgSrc ? (
          <Img src={beforeImgSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background: "linear-gradient(180deg, #374151 0%, #111827 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#EF4444",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 36,
              fontWeight: 800,
            }}
          >
            {beforeLabel}
          </div>
        )}
        <div
          style={{
            position: "absolute",
            top: 60,
            left: 50,
            padding: "10px 22px",
            borderRadius: 999,
            backgroundColor: "rgba(239, 68, 68, 0.9)",
            color: "#FFFFFF",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 20,
            fontWeight: 800,
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
          }}
        >
          {beforeLabel}
        </div>
      </AbsoluteFill>

      {/* Capa 2: ESCENARIO B (Después) con clipPath animado */}
      <AbsoluteFill
        style={{
          clipPath: `inset(0 0 ${100 - cutPercent}% 0)`,
        }}
      >
        {afterImgSrc ? (
          <Img src={afterImgSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background: "linear-gradient(180deg, #065F46 0%, #064E3B 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#10B981",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 36,
              fontWeight: 800,
            }}
          >
            {afterLabel}
          </div>
        )}
        <div
          style={{
            position: "absolute",
            top: 60,
            right: 50,
            padding: "10px 22px",
            borderRadius: 999,
            backgroundColor: "rgba(16, 185, 129, 0.9)",
            color: "#FFFFFF",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 20,
            fontWeight: 800,
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
          }}
        >
          {afterLabel}
        </div>
      </AbsoluteFill>

      {/* Línea divisoria luminosa animada */}
      {cutPercent > 1 && cutPercent < 99 && (
        <div
          style={{
            position: "absolute",
            top: `${cutPercent}%`,
            left: 0,
            right: 0,
            height: 6,
            backgroundColor: "#FFFFFF",
            boxShadow: "0 0 20px #38BDF8, 0 0 40px #FFFFFF",
            zIndex: 50,
          }}
        />
      )}

      {/* Subtítulos */}
      <SubtitulosWhisper words={words} />
    </AbsoluteFill>
  );
};
