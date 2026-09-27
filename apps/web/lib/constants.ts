/**
 * STORMNET Operational Constants & Color Scales
 */

export const OPERATIONAL_SECTORS = [
  { id: "delhi-ncr", name: "Northwest India (Delhi-NCR Composite)", center: [77.209, 28.6139], zoom: 8.5 },
  { id: "mumbai-konkan", name: "Western Coast (Mumbai-Konkan)", center: [72.8777, 19.076], zoom: 8.5 },
  { id: "kolkata-ganges", name: "East India (Kolkata-Ganges Plain)", center: [88.3639, 22.5726], zoom: 8.5 },
  { id: "western-ghats", name: "South Peninsular & Western Ghats", center: [76.2711, 10.8505], zoom: 8.0 },
] as const;

export const DBZ_SCALE = [
  { label: "15", value: 15, color: "#A8DADC", desc: "Drizzle" },
  { label: "25", value: 25, color: "#457B9D", desc: "Light" },
  { label: "35", value: 35, color: "#2A9D8F", desc: "Moderate" },
  { label: "42", value: 42, color: "#E9C46A", desc: "Heavy" },
  { label: "47", value: 47, color: "#F4A261", desc: "Intense" },
  { label: "52", value: 52, color: "#E76F51", desc: "Severe" },
  { label: "57", value: 57, color: "#D90429", desc: "Hail" },
  { label: "62", value: 62, color: "#9D0208", desc: "Severe Hail" },
  { label: "68+", value: 68, color: "#6A040F", desc: "Cloudburst" },
] as const;

export const SEVERITY_COLORS = {
  GREEN: {
    bg: "bg-[#EDF7ED]",
    border: "border-[#C8E6C9]",
    text: "text-[#1E4620]",
    dot: "bg-[#2E7D32]",
    label: "No Warning",
  },
  YELLOW: {
    bg: "bg-[#FFFBE6]",
    border: "border-[#FFE58F]",
    text: "text-[#724E00]",
    dot: "bg-[#D48806]",
    label: "Watch",
  },
  ORANGE: {
    bg: "bg-[#FFF2E8]",
    border: "border-[#FFBB96]",
    text: "text-[#872900]",
    dot: "bg-[#D4380D]",
    label: "Alert",
  },
  RED: {
    bg: "bg-[#FFF1F0]",
    border: "border-[#FFA39E]",
    text: "text-[#820014]",
    dot: "bg-[#CF1322]",
    label: "Warning",
  },
} as const;
