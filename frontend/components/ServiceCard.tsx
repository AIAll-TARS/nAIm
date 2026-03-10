import Link from "next/link";
import { Service } from "@/lib/api";
import { getAgentReadiness } from "@/lib/readiness";
import { AgentReadinessBadge } from "@/components/AgentReadiness";

const CATEGORY_LABELS: Record<string, string> = {
  tts: "TTS", stt: "STT", llm: "LLM", "image-gen": "Image Gen",
  embeddings: "Embeddings", search: "Search", code: "Code", other: "Other",
};

const PRICING_COLORS: Record<string, string> = {
  free: "text-green-400", per_request: "text-blue-400",
  subscription: "text-purple-400", usage_based: "text-yellow-400",
};

export default function ServiceCard({ service }: { service: Service }) {
  const readiness = getAgentReadiness(service);

  return (
    <Link href={`/services/${service.id}`}>
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-600 transition cursor-pointer">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
                {CATEGORY_LABELS[service.category_slug] || service.category_slug}
              </span>
              {service.verified && (
                <span className="text-xs bg-green-900/40 text-green-400 px-2 py-0.5 rounded-full">verified</span>
              )}
              <AgentReadinessBadge readiness={readiness} />
            </div>
            <h2 className="font-semibold text-white truncate">{service.name}</h2>
            <p className="text-xs text-gray-500 mb-2">{service.canonical_provider}</p>
            <p className="text-sm text-gray-400 line-clamp-2">{service.description}</p>
          </div>
          <div className="text-right shrink-0">
            <p className={`text-xs font-medium ${PRICING_COLORS[service.pricing_model] || "text-gray-400"}`}>
              {service.pricing_model.replace("_", " ")}
            </p>
            <p className="text-xs text-gray-600 mt-1 capitalize">{service.auth_type.replace("_", " ")}</p>
          </div>
        </div>
      </div>
    </Link>
  );
}
