import React from "react";
import { AbsoluteFill, Audio, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface KineticWord {
  text: string;
  weight?: "300" | "700" | "900";
  color?: string;
  scale?: number;
  startFrame: number;
}

export interface KineticHookProps {
  bRollMediaSrc?: string;
  wordsSeq?: KineticWord[];
  supportingText?: string;
  audioSrc?: string;
}

export const KineticHookTemplate: React.FC<KineticHookProps> = ({
  bRollMediaSrc,
  wordsSeq = [
    { text: "ESTO", weight: "300", color: "#FFFFFF", startFrame: 5 },
    { text: "CAMBIA", weight: "900", color: "#38BDF8", startFrame: 22 },
    { text: "TODO", weight: "900", color: "#FACC15", startFrame: 42 },
  ],
  supportingText = "La nueva arquitectura para desarrolladores",
  audioSrc,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Encontrar la palabra activa
  let activeWord = wordsSeq[0];
  for (let i = 0; i < wordsSeq.length; i++) {
    if (frame >= wordsSeq[i].startFrame) {
      activeWord = wordsSeq[i];
    }
  }

  const wordLocalFrame = Math.max(0, frame - activeWord.startFrame);
  const popScale = spring({
    frame: wordLocalFrame,
    fps,
    config: { damping: 10, mass: 0.4 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B0F19",
        overflow: "hidden",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <ReadingProgressBar color="#38BDF8" />
      {audioSrc && <Audio src={audioSrc} />}

      {/* 1. Fondo: B-Roll oscuro o dinámico con viñeta */}
      <AbsoluteFill>
        {bRollMediaSrc ? (
          <video
            src={bRollMediaSrc}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background:
                "radial-gradient(circle at 50% 50%, #1E293B 0%, #030712 100%)",
            }}
          />
        )}
        {/* Viñeta para concentrar la atención en el centro */}
        <AbsoluteFill
          style={{
            background:
              "radial-gradient(circle at 50% 50%, transparent 40%, rgba(0,0,0,0.85) 100%)",
          }}
        />
      </AbsoluteFill>

      {/* 2. Centro: Tipografía Cinética Gigante */}
      <div
        style={{
          position: "absolute",
          top: "40%",
          left: 40,
          right: 40,
          transform: "translateY(-50%)",
          textAlign: "center",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 50,
        }}
      >
        <div
          key={activeWord.text}
          style={{
            fontSize: 140,
            fontWeight: (activeWord.weight || "900") as any,
            color: activeWord.color || "#FFFFFF",
            letterSpacing: "-0.04em",
            lineHeight: 1.0,
            textTransform: "uppercase",
            transform: `scale(${popScale * (activeWord.scale || 1.0)})`,
            textShadow:
              "0 10px 40px rgba(0,0,0,0.9), 0 0 40px rgba(56, 189, 248, 0.4)",
          }}
        >
          {activeWord.text}
        </div>

        {/* Subtítulo de apoyo inferior */}
        <div
          style={{
            marginTop: 48,
            fontSize: 26,
            fontWeight: 600,
            color: "#94A3B8",
            letterSpacing: "0.02em",
            maxWidth: 800,
            lineHeight: 1.4,
          }}
        >
          {supportingText}
        </div>
      </div>
    </AbsoluteFill>
  );
};
