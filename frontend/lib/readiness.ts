import { RatingAggregated, Service } from "@/lib/api";

export type ReadinessSignal = {
  label: string;
  ok: boolean;
  note: string;
  weight: number;
};

export type AgentReadiness = {
  score: number;
  grade: string;
  label: "verified" | "needs_review" | "stale";
  signals: ReadinessSignal[];
};

function toGrade(score: number) {
  if (score >= 90) return "A";
  if (score >= 80) return "B";
  if (score >= 70) return "C";
  if (score >= 60) return "D";
  return "E";
}

export function getAgentReadiness(service: Service, ratings?: RatingAggregated | null): AgentReadiness {
  const hasHttpsDocs = /^https:\/\//i.test(service.docs_url || "");
  const hasBaseUrl = /^https?:\/\//i.test(service.base_url || "");
  const authClear = ["api_key", "oauth", "none"].includes(service.auth_type);
  const pricingClear = ["free", "per_request", "subscription", "usage_based"].includes(service.pricing_model);

  const ratingStrong = !!ratings && ratings.count > 0 && ratings.avg_overall >= 3.5;
  const ratingModerate = !!ratings && ratings.count > 0 && ratings.avg_overall >= 2.8;

  const signals: ReadinessSignal[] = [
    {
      label: "Docs link",
      ok: hasHttpsDocs,
      note: hasHttpsDocs ? "HTTPS docs URL present" : "Missing/invalid docs URL",
      weight: 20,
    },
    {
      label: "Base URL",
      ok: hasBaseUrl,
      note: hasBaseUrl ? "API base URL present" : "Missing/invalid base URL",
      weight: 15,
    },
    {
      label: "Auth clarity",
      ok: authClear,
      note: authClear ? `Auth: ${service.auth_type}` : "Auth method unclear",
      weight: 20,
    },
    {
      label: "Pricing clarity",
      ok: pricingClear,
      note: pricingClear ? `Pricing: ${service.pricing_model}` : "Pricing model unclear",
      weight: 20,
    },
    {
      label: "Registry verification",
      ok: service.verified,
      note: service.verified ? "Manually verified in registry" : "Not verified yet",
      weight: 15,
    },
    {
      label: "Agent ratings",
      ok: ratingStrong,
      note: !ratings || ratings.count === 0
        ? "No ratings yet"
        : ratingStrong
          ? `Strong rating (${ratings.avg_overall.toFixed(2)}/5)`
          : ratingModerate
            ? `Mixed rating (${ratings.avg_overall.toFixed(2)}/5)`
            : `Weak rating (${ratings.avg_overall.toFixed(2)}/5)`,
      weight: 10,
    },
  ];

  const score = Math.round(
    signals.reduce((sum, s) => {
      if (s.label === "Agent ratings") {
        if (!ratings || ratings.count === 0) return sum + s.weight * 0.35;
        if (ratingStrong) return sum + s.weight;
        if (ratingModerate) return sum + s.weight * 0.6;
        return sum + s.weight * 0.2;
      }
      return sum + (s.ok ? s.weight : 0);
    }, 0)
  );

  const label: AgentReadiness["label"] = service.verified
    ? "verified"
    : score >= 70
      ? "needs_review"
      : "stale";

  return {
    score,
    grade: toGrade(score),
    label,
    signals,
  };
}
