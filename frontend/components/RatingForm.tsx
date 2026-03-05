"use client";
import { useState } from "react";

interface Props {
  onSubmit: (payload: {
    cost_score: number;
    quality_score: number;
    latency_score: number;
    reliability_score: number;
    agent_id?: string;
    notes?: string;
  }) => Promise<void>;
}

const FIELDS = [
  { key: "quality_score", label: "Quality" },
  { key: "latency_score", label: "Latency" },
  { key: "reliability_score", label: "Reliability" },
  { key: "cost_score", label: "Cost" },
] as const;

export default function RatingForm({ onSubmit }: Props) {
  const [scores, setScores] = useState({ quality_score: 3, latency_score: 3, reliability_score: 3, cost_score: 3 });
  const [agentId, setAgentId] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit({ ...scores, agent_id: agentId || undefined, notes: notes || undefined });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 className="font-semibold mb-4">Rate this service</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        {FIELDS.map(({ key, label }) => (
          <div key={key} className="flex items-center gap-4">
            <span className="text-sm text-gray-400 w-24 shrink-0">{label}</span>
            <input
              type="range" min={1} max={5} step={0.5}
              value={scores[key]}
              onChange={(e) => setScores((s) => ({ ...s, [key]: parseFloat(e.target.value) }))}
              className="flex-1 accent-white"
            />
            <span className="text-sm text-gray-300 w-8 text-right">{scores[key]}</span>
          </div>
        ))}

        <input
          type="text"
          placeholder="Agent ID (optional)"
          value={agentId}
          onChange={(e) => setAgentId(e.target.value)}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm placeholder-gray-500 focus:outline-none focus:border-gray-500"
        />
        <textarea
          placeholder="Notes (optional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm placeholder-gray-500 focus:outline-none focus:border-gray-500 resize-none"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-white text-gray-900 font-medium text-sm py-2 rounded-lg hover:bg-gray-200 transition disabled:opacity-50"
        >
          {loading ? "Submitting..." : "Submit Rating"}
        </button>
      </form>
    </div>
  );
}
