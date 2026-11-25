import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface HighlighterStrokeProps {
  children: React.ReactNode;
  startFrame?: number;
  durationFrames?: number;
  color?: string;
  heightPercent?: number;
}

export const HighlighterStroke: React.FC<HighlighterStrokeProps> = ({
  children,
  startFrame = 15,
  durationFrames = 25,
  color = "#FACC15",
  heightPercent = 45,
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(
    frame,
    [startFrame, startFrame + durationFrames],
    [0, 100],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  return (
    <span
      style={{
        position: "relative",
        display: "inline-block",
        zIndex: 1,
      }}
    >
      <span
        style={{
          position: "absolute",
          left: 0,
          bottom: 4,
          height: `${heightPercent}%`,
          width: `${progress}%`,
          backgroundColor: color,
          opacity: 0.85,
          borderRadius: 4,
          zIndex: -1,
          transition: "width 0.05s ease-out",
        }}
      />
      {children}
    </span>
  );
};
