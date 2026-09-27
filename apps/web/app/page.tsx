import { AppShell } from "@/components/layout/AppShell";
import { SAMPLE_STORMS } from "@/data/sample/storms";

export default function HomePage() {
  return <AppShell initialStorms={SAMPLE_STORMS} />;
}
