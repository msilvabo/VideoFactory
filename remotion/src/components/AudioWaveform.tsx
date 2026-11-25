import React from "react";
import { useCurrentFrame } from "remotion";

export interface AudioWaveformProps {
  barCount?: number;
  height?: number;
  activeColor?: string;
  baseColor?: string;
  waveformValues?: number[];
}

export const AudioWaveform: React.FC<AudioWaveformProps> = ({
  barCount = 28,
  height = 64,
  activeColor = "#38BDF8",
  baseColor = "rgba(56, 189, 248, 0.25)",
  waveformValues,
}) => {
  const frame = useCurrentFrame();

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 5,
        height,
      }}
    >
      {Array.from({ length: barCount }).map((_, i) => {
        let barHeight = 12;
        if (waveformValues && waveformValues.length > 0) {
          const idx = (frame * 2 + i) % waveformValues.length;
          barHeight = Math.max(8, waveformValues[idx] * height);
        } else {
          // Generador armónico orgánico dinámico cuando no hay JSON de envolvente
          const wave =
            Math.sin(frame * 0.25 + i * 0.45) * 0.5 +
            Math.cos(frame * 0.15 - i * 0.2) * 0.5;
          barHeight = Math.max(8, Math.abs(wave) * height);
        }

        return (
          <div
            key={i}
            style={{
              width: 5,
              height: barHeight,
              borderRadius: 3,
              backgroundColor: barHeight > height * 0.5 ? activeColor : baseColor,
              boxShadow:
                barHeight > height * 0.6
                  ? `0 0 10px ${activeColor}`
                  : "none",
              transition: "height 0.06s ease-out",
            }}
          />
        );
      })}
    </div>
  );
};
