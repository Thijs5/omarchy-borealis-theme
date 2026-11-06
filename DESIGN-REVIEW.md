# Visual review — translucent veil revision

The previous curtain retained hard internal colour steps and a short lower
falloff. That made its panels look solid. This revision changes the light
rendering while retaining the landmark drawings, logical pixel grid, theme
palette and horizontal wordmark animation.

## Corrections

- Removed the nine-level aurora palette thresholds that created contour blocks.
  Emission now fades gradually between logical pixels.
- Replaced opaque colour selection with additive RGB light over the night sky.
  Stars remain visible, and green/rose overlap mixes without a hard colour seam.
- Removed the visibility cutoff that gave faint light a distinct outer boundary.
- Extended the lower fade from three to fourteen logical pixels. The light
  dissipates through the hem rather than ending at a sharp rim.
- Reduced contrast between pleats and fine strands. Broader, fainter local
  highlights replace the narrow bright beams.
- Evaluated emission over the full canvas, avoiding a rectangular limit on the
  lower light field before the terrain is composited.

Vestrahorn was inspected first. All four landscape skies were then checked at
0, 10, 20 and 30 seconds. The logo retains the existing horizontal-layer motion.

## Pixel treatment

The glow uses fine RGB gradations at the original 320 × 200 logical resolution.
Each logical pixel still becomes one flat 8 × 8 block in the full-resolution
output. The terrain and letters keep their hard colour clusters. No Gaussian
blur, resampling blur or edge antialiasing is used. A gradual light field can
therefore coexist with crisp pixel geometry.

The veil is deliberately faint. Desktop brightness and display contrast affect
how much of its upper light is visible; the strongest regions carry its motion
while the quieter portions retain substantial dark sky.

## Borealis: color and sky review

The UI palette raises muted text and adjusts red, magenta and brown. App-specific
overrides separate muted text from filled controls and tags; keyboard focus
has a full-contrast teal outline. The measured default-surface checks are in
`reports/readability.json`. The Neovim check resolves Aether v3 highlights in
a headless session, including plugin highlights and selected menus.

The decorative random star field has been replaced by catalogue projections.
Cassiopeia, the Big Dipper and the Little Dipper have documented star positions
and guide paths in `reports/sky-map.json`; those guide lines do not appear in
the exported wallpapers. Each landscape includes one short meteor. Tests count
one contiguous visible event per 40-second loop and keep primary stars and
meteor trajectories clear of the terrain.

## Individual colour moods

Vestrahorn retains its emerald light. The lagoon shifts to rose-violet with
cool teal above; Kirkjufell shifts to mint-teal; Svartifoss shifts to violet
with a broad, restrained emerald contribution. These edits change the emitted
light colours, not the accepted veil paths, pleats, brightness fields or timing.
Reflections inherit the revised sky colours. Terrain, stars and the readable
teal-accent UI palette are preserved.

The wordmark now includes the full colour family. Its horizontal sheets are
ordered from red at the top through broad green/mint and teal/blue to violet
and pink at the bottom, following typical emission altitudes as explained by
NASA (https://science.nasa.gov/sun/auroras/). This is a stylized altitude stack;
natural emissions overlap and do not have a universal rainbow order. Green
occupies most of the letters, with narrower red and nitrogen-coloured fringes.
The original mask and solid background/counters remain unchanged.

## Logo veil correction

The flat multicolour version read as striped lettering: dusty reds, a large
mint stripe and narrow blue/purple bands had fixed opaque boundaries. Slow
movement of those boundaries did not make the fill resemble an auroral veil.

The logo now clips the landscape veil's continuous light-field model into its
original mask. Hanging strands and broad pleats carry changing luminosity;
faint coloured light preserves the letter shapes through the darker gaps.
Overlapping red, green, teal, blue, violet and pink regions flow horizontally
without discrete band edges. Mint highlights emerge only in concentrated
strands. All light is still evaluated on the fixed logical pixel grid: no
image-space blur or antialiasing is applied, and nothing escapes the letters.
