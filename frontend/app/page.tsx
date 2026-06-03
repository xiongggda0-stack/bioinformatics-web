import HeroSection from "@/components/home/HeroSection";
import ModuleGrid from "@/components/home/ModuleGrid";
import QuickTags from "@/components/home/QuickTags";
import RecentUpdates from "@/components/home/RecentUpdates";

export default function HomePage(): JSX.Element {
  return (
    <main>
      <HeroSection />
      <ModuleGrid />
      <QuickTags />
      <RecentUpdates />
      <footer className="border-t border-slate-100 bg-white py-8">
        <div className="mx-auto max-w-7xl px-6">
          <p className="text-xs text-slate-400">
            Bioinformatics Workbench / 2026
          </p>
        </div>
      </footer>
    </main>
  );
}
