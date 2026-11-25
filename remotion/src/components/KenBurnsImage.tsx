import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface KenBurnsImageProps {
  src?: string;
  zoomDirection?: "in" | "out";
  panDirection?: "left-to-right" | "right-to-left" | "none";
  maxScale?: number;
  style?: React.CSSProperties;
  borderRadius?: number;
  fallbackGradient?: string;
}

export const KenBurnsImage: React.FC<KenBurnsImageProps> = ({
  src,
  zoomDirection = "in",
  panDirection = "left-to-right",
  maxScale = 1.10,
  style,
  borderRadius = 16,
  fallbackGradient = "linear-gradient(135deg, #1E293B 0%, #0F172A 100%)",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const scale =
    zoomDirection === "in"
      ? interpolate(frame, [0, durationInFrames], [1.0, maxScale], {
          extrapolateRight: "clamp",
        })
      : interpolate(frame, [0, durationInFrames], [maxScale, 1.0], {
          extrapolateRight: "clamp",
        });

  let translateX = 0;
  if (panDirection === "left-to-right") {
    translateX = interpolate(frame, [0, durationInFrames], [-12, 12]);
  } else if (panDirection === "right-to-left") {
    translateX = interpolate(frame, [0, durationInFrames], [12, -12]);
  }

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        borderRadius,
        ...style,
      }}
    >
      {src ? (
        <Img
          src={src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale}) translateX(${translateX}px)`,
            transformOrigin: "center center",
          }}
        />
      ) : (
        <div
          style={{
            width: "100%",
            height: "100%",
            background: fallbackGradient,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transform: `scale(${scale})`,
          }}
        >
          <div
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 24,
              color: "#38BDF8",
              letterSpacing: "0.1em",
            }}
          >
            [ IMAGEN / B-ROLL ]
          </div>
        </div>
      )}
    </div>
  );
};
