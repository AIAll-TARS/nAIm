export default function RatingBar({ label, value }: { label: string; value: number }) {
  const pct = ((value - 1) / 4) * 100;
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-400 w-20 shrink-0">{label}</span>
      <div className="flex-1 bg-gray-800 rounded-full h-1.5">
        <div className="bg-white rounded-full h-1.5 transition-all" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-400 w-8 text-right">{value.toFixed(1)}</span>
    </div>
  );
}
