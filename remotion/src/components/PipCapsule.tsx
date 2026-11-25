import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface PipCapsuleProps {
  src?: string;
  width?: number;
  height?: number;
  bottom?: number;
  right?: number;
  label?: string;
  borderColor?: string;
}

export const PipCapsule: React.FC<PipCapsuleProps> = ({
  src,
  width = 240,
  height = 340,
  bottom = 120,
  right = 48,
  label = "CAM",
  borderColor = "#38BDF8",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enterScale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom,
        right,
        width,
        height,
        borderRadius: 36,
        overflow: "hidden",
        border: `3px solid ${borderColor}`,
        boxShadow: "0 16px 36px rgba(0, 0, 0, 0.75), 0 0 20px rgba(56, 189, 248, 0.25)",
        backgroundColor: "#111827",
        transform: `scale(${enterScale})`,
        zIndex: 80,
      }}
    >
      {src ? (
        <img
          src={src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
          alt="webcam"
        />
      ) : (
        <div
          style={{
            width: "100%",
            height: "100%",
            background: "linear-gradient(180deg, #1E293B 0%, #0B0F19 100%)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            color: "#94A3B8",
          }}
        >
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: "50%",
              backgroundColor: "rgba(56, 189, 248, 0.15)",
              border: "2px solid #38BDF8",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 12,
            }}
          >
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                backgroundColor: "#EF4444",
              }}
            />
          </div>
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 14,
              letterSpacing: "0.15em",
              color: "#38BDF8",
            }}
          >
            {label}
          </span>
        </div>
      )}
    </div>
  );
};
