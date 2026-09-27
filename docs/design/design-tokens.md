# STORMNET — Design System & Design Tokens
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084  
**Design Theme:** Light Cream / Matte Cartographic Weather Intelligence (IMD/MoES Standard)  
**File Reference:** `docs/design/design-tokens.md`

---

## 1. Color Palette Tokens

The color palette is engineered specifically for long-duration forecaster operational shifts. It replaces stark harsh white `#FFFFFF` backgrounds with restful, warm-toned matte surfaces (`#FAF8F5`, `#F5F2EC`), paired with deep slate typography and scientifically calibrated IMD hazard colors.

### 1.1 Canvas & Surface Tokens (Matte Cream Substrates)

| Token Name | Hex Value | CSS Variable | Semantic Usage |
| :--- | :--- | :--- | :--- |
| `surface-canvas` | `#FAF8F5` | `--color-surface-canvas` | Main application background behind panels |
| `surface-card` | `#FFFFFF` | `--color-surface-card` | Cards, panels, active content surfaces |
| `surface-subtle` | `#F4F0E8` | `--color-surface-subtle` | Inset backgrounds, table headers, timeline track |
| `surface-muted` | `#ECE7DC` | `--color-surface-muted` | Inactive elements, hover states, secondary chips |
| `surface-overlay` | `rgba(250, 248, 245, 0.88)` | `--color-surface-overlay` | Floating HUD panels (with subtle backdrop blur) |

### 1.2 Border & Divider Tokens

| Token Name | Hex Value | CSS Variable | Semantic Usage |
| :--- | :--- | :--- | :--- |
| `border-subtle` | `#E8E2D8` | `--color-border-subtle` | Internal card dividers, table row borders |
| `border-default` | `#D8D1C4` | `--color-border-default` | Standard panel borders, container outlines |
| `border-strong` | `#B8AE9D` | `--color-border-strong` | Active input fields, selected cell outlines |
| `border-focus` | `#1E3A5F` | `--color-border-focus` | Keyboard accessibility focus rings (2px solid) |

### 1.3 Text & Typographic Colors

| Token Name | Hex Value | CSS Variable | Semantic Usage |
| :--- | :--- | :--- | :--- |
| `text-primary` | `#1C1917` | `--color-text-primary` | Headers, primary titles, critical metrics |
| `text-secondary` | `#44403C` | `--color-text-secondary` | Body text, panel descriptions, sensor labels |
| `text-muted` | `#78716C` | `--color-text-muted` | Units (dBZ, km/h), secondary timestamps, captions |
| `text-disabled` | `#A8A29E` | `--color-text-disabled` | Inactive timeline marks, disabled buttons |
| `text-inverse` | `#FFFFFF` | `--color-text-inverse` | Text on dark buttons, badges, or red alerts |

### 1.4 Brand & Meteorological Authority Accents

| Token Name | Hex Value | CSS Variable | Semantic Usage |
| :--- | :--- | :--- | :--- |
| `brand-navy-900` | `#0F1D30` | `--color-brand-navy-900` | Deepest brand accent, primary button hover |
| `brand-navy-800` | `#1E3A5F` | `--color-brand-navy-800` | Primary brand identity, active tabs, header title |
| `brand-navy-700` | `#2D5385` | `--color-brand-navy-700` | Secondary interactive links, vector arrow color |
| `brand-navy-100` | `#EBF1F8` | `--color-brand-navy-100` | Active selection pill background |

### 1.5 IMD Four-Stage Hazard Warning System Tokens

| Level | Severity | Background | Border | Text | Badge Fill |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **No Warning** | **Green** | `#EDF7ED` | `#C8E6C9` | `#1E4620` | `#2E7D32` |
| **Watch** | **Yellow** | `#FFFBE6` | `#FFE58F` | `#724E00` | `#D48806` |
| **Alert** | **Orange** | `#FFF2E8` | `#FFBB96` | `#872900` | `#D4380D` |
| **Warning** | **Red** | `#FFF1F0` | `#FFA39E` | `#820014` | `#CF1322` |

### 1.6 Calibrated Doppler Radar Reflectivity (dBZ) Scale

Calibrated for maximum contrast against a light cream/matte map base (avoiding low-contrast yellows and washed-out pastels):

| dBZ Range | Precipitation Phenomenon | Hex Value | CSS Variable |
| :--- | :--- | :--- | :--- |
| **< 15 dBZ** | Non-precipitating / Clear Air | `transparent` | `--dbz-00` |
| **15 – 20 dBZ** | Very Light Rain / Drizzle | `#A8DADC` | `--dbz-15` |
| **20 – 30 dBZ** | Light Precipitation | `#457B9D` | `--dbz-25` |
| **30 – 40 dBZ** | Moderate Rain / Developing Cloud | `#2A9D8F` | `--dbz-35` |
| **40 – 45 dBZ** | Heavy Rain / Convective Updraft | `#E9C46A` | `--dbz-42` |
| **45 – 50 dBZ** | Very Heavy Rain / Hail Initiation | `#F4A261` | `--dbz-47` |
| **50 – 55 dBZ** | Severe Thunderstorm / Small Hail | `#E76F51` | `--dbz-52` |
| **55 – 60 dBZ** | Damaging Hail / Torrential Cloudburst | `#D90429` | `--dbz-57` |
| **60 – 65 dBZ** | Extreme Hail Core (>3 cm) | `#9D0208` | `--dbz-62` |
| **> 65 dBZ** | Violent Cloudburst / Giant Hail | `#6A040F` | `--dbz-68` |

---

## 2. Typography System

The typography uses high-legibility geometric sans-serif for UI chrome combined with tabular monospaced numbers for meteorological coordinates, timestamps, and physical measurements.

### 2.1 Font Families

```css
:root {
  /* Primary interface font: clean, humanist-neutral, high x-height */
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  
  /* Meteorological & numeric font: strict tabular figures, zero-ambiguity characters */
  --font-mono: "JetBrains Mono", "SF Mono", "Roboto Mono", Consolas, monospace;
}
```

### 2.2 Typographic Hierarchy Scale

| Token | Size | Line Height | Weight | Letter Spacing | Target Elements |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `--text-xs` | `11px` (`0.6875rem`) | `14px` | `500` Medium | `+0.02em` | Axis ticks, sensor status labels, micro-units |
| `--text-sm` | `12px` (`0.75rem`) | `16px` | `400` / `500` | `0` | Coordinate readouts, cell attributes, descriptions |
| `--text-base` | `13px` (`0.8125rem`) | `18px` | `400` / `600` | `-0.01em` | Standard UI labels, body text, buttons |
| `--text-md` | `14px` (`0.875rem`) | `20px` | `600` SemiBold | `-0.01em` | Section headers, card titles, dropdown triggers |
| `--text-lg` | `16px` (`1.0rem`) | `22px` | `600` SemiBold | `-0.015em` | Panel titles, alert banner headings |
| `--text-xl` | `20px` (`1.25rem`) | `26px` | `700` Bold | `-0.02em` | Primary metric readouts (e.g. `61.5 dBZ`, `84%`) |
| `--text-2xl` | `24px` (`1.5rem`) | `30px` | `700` Bold | `-0.02em` | Main application wordmark |

---

## 3. Spacing & Sizing System

Based on a strict **4px modular grid** to guarantee optical alignment across map controls, panels, and tables.

```css
:root {
  --space-0-5: 2px;
  --space-1:   4px;
  --space-1-5: 6px;
  --space-2:   8px;
  --space-2-5: 10px;
  --space-3:   12px;
  --space-4:   16px;
  --space-5:   20px;
  --space-6:   24px;
  --space-8:   32px;
  --space-10:  40px;
  --space-12:  48px;
  --space-16:  64px;
}
```

### Component Height Standards
- **Header Navigation Bar:** `52px`
- **Timeline Scrubber Height:** `64px`
- **Standard Button Height:** `32px` (compact: `26px`, large: `38px`)
- **Badge / Pill Height:** `20px`
- **Right Panel Width:** `380px` (desktop), `340px` (laptop)

---

## 4. Border Radius System

Intentionally restrained and square-leaning to project formal, technical government credibility. Bubbly or rounded-xl mobile styling is avoided.

```css
:root {
  --radius-none: 0px;
  --radius-xs:   2px;  /* Metric tags, small badges */
  --radius-sm:   4px;  /* Buttons, text inputs, timeline markers */
  --radius-md:   6px;  /* Standard cards, dropdowns, HUD overlays */
  --radius-lg:   8px;  /* Main panels, modals */
  --radius-full: 9999px; /* Status indicator dots, round icons */
}
```

---

## 5. Shadow & Elevation System (Matte Atmospheric)

Avoids heavy, dark, or glowing drop shadows. Employs soft warm-tinted ambient diffusion that feels like layered paper sheets.

```css
:root {
  /* Level 0: Flat on canvas (no shadow) */
  --shadow-none: none;

  /* Level 1: Subtle separation for inner cards and inputs */
  --shadow-xs: 0 1px 2px 0 rgba(28, 25, 23, 0.04);

  /* Level 2: Standard card & panel elevation */
  --shadow-sm: 0 1px 3px 0 rgba(28, 25, 23, 0.06), 0 1px 2px -1px rgba(28, 25, 23, 0.04);

  /* Level 3: Floating map HUD controls & Timeline bar */
  --shadow-md: 0 4px 8px -2px rgba(28, 25, 23, 0.08), 0 2px 4px -2px rgba(28, 25, 23, 0.05);

  /* Level 4: Lateral inspection panel, dropdown menus */
  --shadow-lg: 0 8px 16px -4px rgba(28, 25, 23, 0.09), 0 4px 6px -3px rgba(28, 25, 23, 0.05);

  /* Level 5: Emergency Warning banners & modal dialogs */
  --shadow-xl: 0 12px 24px -6px rgba(28, 25, 23, 0.12), 0 6px 10px -4px rgba(28, 25, 23, 0.07);
}
```

---

## 6. Z-Index Layering Registry

Prevents map overlay collisions and floating HUD clipping:

```css
:root {
  --z-map-base:       0;
  --z-map-rasters:    5;  /* Radar reflectivity tiles */
  --z-map-vectors:    10; /* Cell contours, motion arrows */
  --z-map-markers:    15; /* AWS stations, lightning strikes */
  --z-map-hud:        25; /* Coordinate HUD, zoom buttons, dBZ scale */
  --z-timeline:       35; /* Floating bottom timeline bar */
  --z-side-panel:     45; /* Right-hand storm inspection panel */
  --z-header:         55; /* Persistent top navigation header */
  --z-dropdown:       65; /* Menus, sector selection popovers */
  --z-modal:          80; /* Alert dispatch modal, CAP exporter */
  --z-tooltip:        100;/* Hover inspect tooltips */
}
```

---

## 7. Motion & Transition System

Micro-interactions are snappy and informative rather than decorative. 

```css
:root {
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-in-out:  cubic-bezier(0.4, 0, 0.2, 1);
  
  --duration-fast:   120ms; /* Button hovers, toggle switches */
  --duration-normal: 200ms; /* Dropdown reveals, badge state changes */
  --duration-slow:   320ms; /* Side panel collapse/expand, drawer slide */
}
```
