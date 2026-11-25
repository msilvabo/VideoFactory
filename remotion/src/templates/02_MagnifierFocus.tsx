import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { PipCapsule } from "../components/PipCapsule";
import { SubtitulosWhisper, WordTimestamp } from "../SubtitulosWhisper";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface MagnifierFocusProps {
  bgImageSrc?: string;
  focusTitle?: string;
  focusSubtitle?: string;
  focusX?: number; // Porcentaje 0 a 100
  focusY?: number; // Porcentaje 0 a 100
  zoomLevel?: number; // ej. 2.0
  startFrame?: number;
  durationFrames?: number;
  webcamSrc?: string;
  audioSrc?: string;
  words?: WordTimestamp[];
}

export const MagnifierFocusTemplate: React.FC<MagnifierFocusProps> = ({
  bgImageSrc,
  focusTitle = "DETALLE DE CÓDIGO",
  focusSubtitle = "Función crítica de alto rendimiento",
  focusX = 50,
  focusY = 40,
  zoomLevel = 2.2,
  startFrame = 20,
  durationFrames = 100,
  webcamSrc,
  audioSrc,
  words,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Activación del zoom magnificador
  const isFocusActive = frame >= startFrame && frame <= startFrame + durationFrames;
  const localFrame = Math.max(0, frame - startFrame);

  const focusProgress = spring({
    frame: isFocusActive ? localFrame : 0,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  const blurAmount = interpolate(focusProgress, [0, 1], [0, 6]);
  const dimBrightness = interpolate(focusProgress, [0, 1], [1.0, 0.55]);

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

      {/* 1. Fondo completo con blur interactivo */}
      <AbsoluteFill
        style={{
          filter: `blur(${blurAmount}px) brightness(${dimBrightness})`,
          transition: "filter 0.1s ease-out",
        }}
      >
        {bgImageSrc ? (
          <Img src={bgImageSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background: "radial-gradient(circle at 50% 40%, #1E293B 0%, #0B0F19 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span style={{ color: "#64748B", fontFamily: "'JetBrains Mono', monospace", fontSize: 26 }}>
              [ FONDO PRINCIPAL / DOCUMENTO ]
            </span>
          </div>
        )}
      </AbsoluteFill>

      {/* 2. Tarjeta Flotante Lupa Magnificadora */}
      {focusProgress > 0.05 && (
        <div
          style={{
            position: "absolute",
            top: 240,
            left: 50,
            right: 50,
            height: 640,
            borderRadius: 32,
            overflow: "hidden",
            border: "3px solid #38BDF8",
            boxShadow: "0 30px 60px rgba(0, 0, 0, 0.8), 0 0 35px rgba(56, 189, 248, 0.4)",
            transform: `scale(${focusProgress})`,
            transformOrigin: `${focusX}% ${focusY}%`,
            zIndex: 60,
            backgroundColor: "#0F172A",
          }}
        >
          {/* Imagen ampliada enfocada */}
          <div
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              overflow: "hidden",
            }}
          >
            {bgImageSrc ? (
              <Img
                src={bgImageSrc}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  transform: `scale(${zoomLevel})`,
                  transformOrigin: `${focusX}% ${focusY}%`,
                }}
              />
            ) : (
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#38BDF8",
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 28,
                  fontWeight: 700,
                }}
              >
                ZOOM {zoomLevel}X [{focusX}%, {focusY}%]
              </div>
            )}

            {/* Cabecera tech estilo píldora */}
            <div
              style={{
                position: "absolute",
                top: 20,
                left: 20,
                right: 20,
                padding: "14px 20px",
                borderRadius: 18,
                backgroundColor: "rgba(11, 15, 25, 0.85)",
                backdropFilter: "blur(14px)",
                border: "1px solid rgba(56, 189, 248, 0.3)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 16,
                    color: "#38BDF8",
                    fontWeight: 800,
                  }}
                >
                  {focusTitle}
                </div>
                <div style={{ fontSize: 14, color: "#CBD5E1", marginTop: 2 }}>
                  {focusSubtitle}
                </div>
              </div>
              <div
                style={{
                  padding: "4px 10px",
                  borderRadius: 999,
                  backgroundColor: "#EF4444",
                  color: "#FFFFFF",
                  fontSize: 12,
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: 700,
                }}
              >
                LIVE ZOOM
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3. Webcam en Cápsula PiP vertical */}
      <PipCapsule src={webcamSrc} bottom={320} right={48} width={240} height={320} />

      {/* 4. Subtítulos */}
      <SubtitulosWhisper words={words} />
    </AbsoluteFill>
  );
};
