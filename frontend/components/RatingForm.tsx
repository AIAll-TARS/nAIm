"use client";
import axios from "axios";
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

const SCORE_MIN = 1;
const SCORE_MAX = 5;
const SCORE_STEP = 0.5;

const FIELDS = [
  { key: "quality_score", label: "Quality", hint: "Output usefulness" },
  { key: "latency_score", label: "Latency", hint: "Response speed" },
  { key: "reliability_score", label: "Reliability", hint: "Consistency / uptime" },
  { key: "cost_score", label: "Cost", hint: "5 = cheap/free, 1 = expensive" },
] as const;

type ScoreKey = (typeof FIELDS)[number]["key"];

function extractErrorMessage(err: unknown) {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: unknown } | undefined)?.detail;
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => (item && typeof item === "object" ? (item as { msg?: string }).msg : undefined))
        .filter((msg): msg is string => Boolean(msg));
      if (messages.length) return messages.join(" ");
    }
    if (typeof detail === "string") return detail;
    if (err.message) return err.message;
  }
  return "Could not submit rating. Please try again.";
}

export default function RatingForm({ onSubmit }: Props) {
  const [scores, setScores] = useState({ quality_score: 3, latency_score: 3, reliability_score: 3, cost_score: 3 });
  const [agentId, setAgentId] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setScore = (key: ScoreKey, value: number) => {
    const clamped = Math.max(SCORE_MIN, Math.min(SCORE_MAX, value));
    setScores((s) => ({ ...s, [key]: clamped }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await onSubmit({ ...scores, agent_id: agentId || undefined, notes: notes || undefined });
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 className="font-semibold mb-2">Rate this service</h3>
      <p className="text-xs text-gray-400 mb-4">
        Scale is <span className="text-gray-200">1.0 to 5.0</span> (0.5 steps). Higher is better. For cost, 5 means
        cheap or free.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        {FIELDS.map(({ key, label, hint }) => (
          <div key={key} className="flex items-center gap-4">
            <div className="w-36 shrink-0">
              <p className="text-sm text-gray-300">{label}</p>
              <p className="text-[11px] text-gray-500 leading-tight">{hint}</p>
            </div>
            <input
              type="range"
              min={SCORE_MIN}
              max={SCORE_MAX}
              step={SCORE_STEP}
              value={scores[key]}
              onChange={(e) => setScore(key, parseFloat(e.target.value))}
              className="flex-1 accent-white"
            />
            <span className="text-sm text-gray-300 w-12 text-right">{scores[key].toFixed(1)}</span>
          </div>
        ))}

        <div className="text-[11px] text-gray-500 flex justify-between px-1">
          <span>{SCORE_MIN} = poor</span>
          <span>{SCORE_MAX} = excellent</span>
        </div>

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

        {error && (
          <p className="text-xs text-red-400 bg-red-900/20 border border-red-800 rounded-lg px-3 py-2">{error}</p>
        )}

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
