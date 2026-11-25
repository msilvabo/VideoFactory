import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface ReadingProgressBarProps {
  color?: string;
  height?: number;
  position?: "top" | "bottom";
}

export const ReadingProgressBar: React.FC<ReadingProgressBarProps> = ({
  color = "#38BDF8",
  height = 8,
  position = "top",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: position === "top" ? 0 : "auto",
        bottom: position === "bottom" ? 0 : "auto",
        left: 0,
        width: "100%",
        height,
        backgroundColor: "rgba(255, 255, 255, 0.08)",
        zIndex: 999,
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: "100%",
          background: `linear-gradient(90deg, ${color} 0%, #10B981 100%)`,
          boxShadow: `0 0 12px ${color}`,
        }}
      />
    </div>
  );
};
