import React from "react";
import { Composition, staticFile } from "remotion";
import { MainComposition, MainCompositionProps } from "./Composition";
import demoSubtitulos from "../public/demo_test/subtitulos.json";

// Importación de los 9 Templates de Alta Retención (9:16)
import { SplitKaraokeTemplate } from "./templates/01_SplitKaraoke";
import { MagnifierFocusTemplate } from "./templates/02_MagnifierFocus";
import { BentoGridTemplate } from "./templates/03_BentoGrid";
import { BeforeAfterTemplate } from "./templates/04_BeforeAfter";
import { PresenterHUDTemplate } from "./templates/05_PresenterHUD";
import { NewsCardWaveformTemplate } from "./templates/06_NewsCardWaveform";
import { VoxHighlighterTemplate } from "./templates/07_VoxHighlighter";
import { KineticHookTemplate } from "./templates/08_KineticHook";
import { SmartReframeTemplate } from "./templates/09_SmartReframe";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Composición Base Multipropósito */}
      <Composition
        id="Main"
        component={MainComposition}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "VideoFactory Studio",
          subtitle: "Pipeline Automatizado de Video Vertical",
          projectSlug: "demo_test",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        } satisfies MainCompositionProps}
      />

      {/* 1. Pantalla Dividida + Karaoke */}
      <Composition
        id="Template01-SplitKaraoke"
        component={SplitKaraokeTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          topTitle: "ANÁLISIS DE ARQUITECTURA",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

      {/* 2. Lupa Magnificadora */}
      <Composition
        id="Template02-MagnifierFocus"
        component={MagnifierFocusTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          focusTitle: "DETALLE DE CÓDIGO",
          focusSubtitle: "Refactorización con Agentes IA",
          focusX: 50,
          focusY: 40,
          zoomLevel: 2.2,
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

      {/* 3. Bento Grid 3X */}
      <Composition
        id="Template03-BentoGrid"
        component={BentoGridTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          headerTitle: "3 PILARES DE ARQUITECTURA",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

      {/* 4. Antes vs. Después */}
      <Composition
        id="Template04-BeforeAfter"
        component={BeforeAfterTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          beforeLabel: "ANTES // MANUAL",
          afterLabel: "DESPUÉS // AUTOMATIZADO",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

      {/* 5. Presentador HUD (Silueta) */}
      <Composition
        id="Template05-PresenterHUD"
        component={PresenterHUDTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          headerBadge: "EXPLICACIÓN // AGENTES IA",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

      {/* 6. Tarjeta Noticia / Pop-Up + Waveform */}
      <Composition
        id="Template06-NewsCardWaveform"
        component={NewsCardWaveformTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          sourceBadge: "TECH RADAR // 2026",
          headline: "Arquitectura Multi-Agente Supera la Programación Convencional",
          quote: "«El desarrollo asistido por agentes autónomos lidera la mayor revolución en ingeniería de software.»",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

      {/* 7. Estilo Vox / Highlighter */}
      <Composition
        id="Template07-VoxHighlighter"
        component={VoxHighlighterTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          publicationName: "SOFTWARE ENGINEERING JOURNAL",
          articleDate: "NOVIEMBRE 2026",
          preText: "Los análisis demuestran que ",
          highlightedText: "la arquitectura dirigida por pruebas y agentes IA acelera el delivery un 80%",
          postText: " sin comprometer la estabilidad en producción.",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

      {/* 8. Tipografía Cinética Explosiva (Hook) */}
      <Composition
        id="Template08-KineticHook"
        component={KineticHookTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          wordsSeq: [
            { text: "ESTO", weight: "300", color: "#FFFFFF", startFrame: 5 },
            { text: "CAMBIA", weight: "900", color: "#38BDF8", startFrame: 20 },
            { text: "TODO", weight: "900", color: "#FACC15", startFrame: 40 },
          ],
          supportingText: "La nueva era de la factoría de video con IA",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
        }}
      />

      {/* 9. Smart Reframe 16:9 a 9:16 */}
      <Composition
        id="Template09-SmartReframe"
        component={SmartReframeTemplate}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          headerHeadline: "DESARROLLO VERTICAL",
          headerSub: "Re-encuadre inteligente de video horizontal",
          audioSrc: staticFile("demo_test/audio_limpio.mp3"),
          words: demoSubtitulos,
        }}
      />

    </>
  );
};
