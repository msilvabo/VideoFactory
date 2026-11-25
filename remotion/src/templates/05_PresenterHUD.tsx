import React from "react";
import { AbsoluteFill, Audio, Img } from "remotion";
import { WordTimestamp } from "../SubtitulosWhisper";
import { ReadingProgressBar } from "../components/ReadingProgressBar";

export interface PresenterHUDProps {
  bgMediaSrc?: string;
  bgType?: "image" | "video";
  silhouetteVideoSrc?: string; // Archivo .webm con alfa generado por extraer_silueta_video.py
  audioSrc?: string;
  words?: WordTimestamp[];
  headerBadge?: string;
}

export const PresenterHUDTemplate: React.FC<PresenterHUDProps> = ({
  bgMediaSrc,
  bgType = "image",
  silhouetteVideoSrc,
  audioSrc,
  words,
  headerBadge = "INFORME // EN DIRECTO",
}) => {
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

      {/* 1. Fondo completo (100%) */}
      <AbsoluteFill>
        {bgMediaSrc ? (
          bgType === "video" ? (
            <video
              src={bgMediaSrc}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : (
            <Img
              src={bgMediaSrc}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          )
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background:
                "radial-gradient(circle at 60% 40%, #1E293B 0%, #0B0F19 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#64748B",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 26,
            }}
          >
            [ B-ROLL / MATERIAL VISUAL COMPLETO ]
          </div>
        )}
      </AbsoluteFill>

      {/* Badge superior tech */}
      <div
        style={{
          position: "absolute",
          top: 50,
          left: 50,
          padding: "10px 22px",
          borderRadius: 999,
          backgroundColor: "rgba(11, 15, 25, 0.8)",
          backdropFilter: "blur(12px)",
          border: "1px solid rgba(56, 189, 248, 0.4)",
          color: "#38BDF8",
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 18,
          fontWeight: 700,
          letterSpacing: "0.1em",
        }}
      >
        {headerBadge}
      </div>

      {/* 2. Primer Plano (Esquina Inferior Izquierda): Silueta del presentador con alfa */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: -40,
          width: 680,
          height: 1050,
          zIndex: 40,
          pointerEvents: "none",
        }}
      >
        {silhouetteVideoSrc ? (
          <video
            src={silhouetteVideoSrc}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "contain",
              filter: "drop-shadow(0 15px 30px rgba(0,0,0,0.85)) drop-shadow(0 0 15px rgba(56,189,248,0.25))",
            }}
          />
        ) : (
          // Representación mock HUD cuando aún no se ha renderizado el WebM alfa
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              flexDirection: "column",
              justifyContent: "flex-end",
              paddingLeft: 60,
              paddingBottom: 80,
            }}
          >
            <div
              style={{
                width: 440,
                height: 720,
                borderRadius: "180px 180px 0 0",
                background:
                  "linear-gradient(180deg, rgba(56, 189, 248, 0.35) 0%, rgba(15, 23, 42, 0.9) 100%)",
                border: "2px solid rgba(56, 189, 248, 0.5)",
                boxShadow:
                  "0 20px 50px rgba(0,0,0,0.9), 0 0 30px rgba(56, 189, 248, 0.3)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                color: "#38BDF8",
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              <div style={{ fontSize: 24, fontWeight: 700 }}>SILUETA ALFA</div>
              <div style={{ fontSize: 16, color: "#94A3B8", marginTop: 8 }}>
                .webm VP9 transparente
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 3. Subtítulos alineados en el espacio libre a la derecha */}
      <div
        style={{
          position: "absolute",
          bottom: 340,
          right: 48,
          width: 440,
          zIndex: 50,
          textAlign: "left",
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(11, 15, 25, 0.75)",
            backdropFilter: "blur(14px)",
            padding: "20px 24px",
            borderRadius: 20,
            border: "1px solid rgba(255, 255, 255, 0.12)",
          }}
        >
          <div
            style={{
              fontSize: 32,
              fontWeight: 800,
              lineHeight: 1.25,
              color: "#FFFFFF",
            }}
          >
            Explicación inmersiva en <span style={{ color: "#38BDF8" }}>tiempo real</span> sobre el contenido.
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
