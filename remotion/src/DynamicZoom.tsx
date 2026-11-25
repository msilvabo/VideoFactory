import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface ZoomPoint {
  startFrame: number;
  scale: number;
  originY?: string;
  originX?: string;
}

export interface DynamicZoomProps {
  children: React.ReactNode;
  zoomPoints?: ZoomPoint[];
}

export const DynamicZoom: React.FC<DynamicZoomProps> = ({
  children,
  zoomPoints = [],
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  let currentScale = 1.0;
  let originY = "50%";
  let originX = "50%";

  if (zoomPoints.length > 0) {
    // Determinar qué punto de zoom está activo
    for (let i = 0; i < zoomPoints.length; i++) {
      const zp = zoomPoints[i];
      if (frame >= zp.startFrame) {
        const nextZp = zoomPoints[i + 1];
        if (!nextZp || frame < nextZp.startFrame) {
          const progress = spring({
            frame: frame - zp.startFrame,
            fps,
            config: { damping: 14, mass: 0.7 },
          });
          const prevScale = i > 0 ? zoomPoints[i - 1].scale : 1.0;
          currentScale = prevScale + (zp.scale - prevScale) * progress;
          originY = zp.originY || "50%";
          originX = zp.originX || "50%";
          break;
        }
      }
    }
  }

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${currentScale})`,
        transformOrigin: `${originX} ${originY}`,
        transition: "transform 0.05s ease-out",
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
