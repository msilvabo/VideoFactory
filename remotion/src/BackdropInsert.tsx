import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface BackdropInsertProps {
  src?: string;
  type?: "image" | "video";
  mode?: "lateral-left" | "lateral-right" | "vertical-top" | "vertical-bottom";
  startFrame?: number;
  durationFrames?: number;
  featherPercent?: number;
  title?: string;
  subtitle?: string;
}

export const BackdropInsert: React.FC<BackdropInsertProps> = ({
  src,
  type = "image",
  mode = "vertical-top",
  startFrame = 30,
  durationFrames = 90,
  featherPercent = 30,
  title = "INSPECCIÓN TÉCNICA",
  subtitle = "Arquitectura de Software",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame < startFrame || frame > startFrame + durationFrames) {
    return null;
  }

  const localFrame = frame - startFrame;
  const enterProgress = spring({
    frame: localFrame,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  const exitOpacity = interpolate(
    localFrame,
    [durationFrames - 15, durationFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        top: mode === "vertical-top" ? 120 : "auto",
        bottom: mode === "vertical-bottom" ? 420 : "auto",
        left: 60,
        right: 60,
        borderRadius: 20,
        backgroundColor: "rgba(15, 23, 42, 0.85)",
        border: "1px solid rgba(56, 189, 248, 0.3)",
        boxShadow: "0 20px 40px rgba(0, 0, 0, 0.6)",
        overflow: "hidden",
        backdropFilter: "blur(12px)",
        opacity: exitOpacity,
        transform: `scale(${enterProgress}) translateY(${(1 - enterProgress) * 30}px)`,
        zIndex: 10,
      }}
    >
      {/* Barra superior estilo macOS / terminal */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "12px 18px",
          backgroundColor: "rgba(30, 41, 59, 0.7)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
        }}
      >
        <span style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#EF4444" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: "#10B981" }} />
        <span
          style={{
            marginLeft: 12,
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 16,
            color: "#94A3B8",
            letterSpacing: "0.08em",
          }}
        >
          {title}
        </span>
      </div>

      {/* Contenido interior */}
      <div style={{ padding: "24px 28px" }}>
        <p
          style={{
            margin: 0,
            fontSize: 24,
            fontWeight: 600,
            color: "#E2E8F0",
            fontFamily: "'Inter', sans-serif",
          }}
        >
          {subtitle}
        </p>
      </div>
    </div>
  );
};
