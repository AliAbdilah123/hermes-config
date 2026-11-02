import { loadFont } from "@remotion/google-fonts/Inter";

// loadFont() blocks the render until the font is fetched — it MUST be called
// at module scope inside the entry point, not in a bare side-effect import.
export const { fontFamily: FONT } = loadFont("normal", {
  weights: ["500", "600", "800"],
  subsets: ["latin"],
  ignoreTooManyRequestsWarning: true,
});
