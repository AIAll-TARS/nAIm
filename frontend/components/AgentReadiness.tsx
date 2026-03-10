import { AgentReadiness } from "@/lib/readiness";

function labelStyle(label: AgentReadiness["label"]) {
  if (label === "verified") return "bg-green-900/40 text-green-300 border-green-800";
  if (label === "needs_review") return "bg-yellow-900/40 text-yellow-300 border-yellow-800";
  return "bg-gray-800 text-gray-300 border-gray-700";
}

export function AgentReadinessBadge({ readiness }: { readiness: AgentReadiness }) {
  return (
    <span
      className={`text-xs px-2 py-0.5 rounded-full border ${labelStyle(readiness.label)}`}
      title={`Agent Readiness ${readiness.score}/100`}
    >
      A-Score {readiness.score}
    </span>
  );
}

export function AgentReadinessPanel({ readiness, updatedAt }: { readiness: AgentReadiness; updatedAt: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold">Agent Readiness</h3>
          <p className="text-xs text-gray-500 mt-1">Composite indicator for API discoverability and operational clarity.</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-white">{readiness.score}</p>
          <p className="text-xs text-gray-500">Grade {readiness.grade}</p>
        </div>
      </div>

      <div className="space-y-2">
        {readiness.signals.map((signal) => (
          <div key={signal.label} className="flex items-start justify-between text-sm border-b border-gray-800 pb-2 last:border-0 last:pb-0">
            <div>
              <p className="text-gray-200">{signal.label}</p>
              <p className="text-xs text-gray-500">{signal.note}</p>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full ${signal.ok ? "bg-green-900/40 text-green-300" : "bg-gray-800 text-gray-400"}`}>
              {signal.ok ? "ok" : "check"}
            </span>
          </div>
        ))}
      </div>

      <p className="text-[11px] text-gray-600 mt-4">Last registry update: {new Date(updatedAt).toLocaleString()}</p>
    </div>
  );
}
