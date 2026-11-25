import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface BentoCardProps {
  title: string;
  subtitle?: string;
  value?: string;
  badge?: string;
  color?: string;
  delayFrames?: number;
  style?: React.CSSProperties;
}

export const BentoCard: React.FC<BentoCardProps> = ({
  title,
  subtitle,
  value,
  badge,
  color = "#38BDF8",
  delayFrames = 0,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delayFrames);
  const enterProgress = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  return (
    <div
      style={{
        borderRadius: 24,
        backgroundColor: "rgba(15, 23, 42, 0.8)",
        border: `1.5px solid ${adjustedFrame > 15 ? color : "rgba(255, 255, 255, 0.1)"}`,
        boxShadow: "0 12px 30px rgba(0, 0, 0, 0.5)",
        backdropFilter: "blur(12px)",
        padding: "24px 28px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        opacity: enterProgress,
        transform: `translateY(${(1 - enterProgress) * 40}px) scale(${0.92 + 0.08 * enterProgress})`,
        overflow: "hidden",
        position: "relative",
        ...style,
      }}
    >
      {badge && (
        <div
          style={{
            alignSelf: "flex-start",
            padding: "4px 12px",
            borderRadius: 999,
            backgroundColor: `${color}20`,
            border: `1px solid ${color}60`,
            color,
            fontSize: 14,
            fontWeight: 700,
            fontFamily: "'JetBrains Mono', monospace",
            letterSpacing: "0.06em",
            marginBottom: 8,
          }}
        >
          {badge}
        </div>
      )}
      <div>
        <h3
          style={{
            margin: 0,
            fontSize: 32,
            fontWeight: 800,
            color: "#FFFFFF",
            fontFamily: "'Inter', sans-serif",
            letterSpacing: "-0.02em",
          }}
        >
          {title}
        </h3>
        {subtitle && (
          <p
            style={{
              margin: "6px 0 0 0",
              fontSize: 18,
              color: "#94A3B8",
              fontFamily: "'Inter', sans-serif",
              lineHeight: 1.3,
            }}
          >
            {subtitle}
          </p>
        )}
      </div>
      {value && (
        <div
          style={{
            fontSize: 48,
            fontWeight: 900,
            color,
            fontFamily: "'JetBrains Mono', monospace",
            marginTop: 12,
          }}
        >
          {value}
        </div>
      )}
    </div>
  );
};
