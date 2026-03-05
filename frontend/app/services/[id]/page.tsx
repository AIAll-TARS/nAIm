"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getService, getRatings, submitRating, Service, RatingAggregated } from "@/lib/api";
import RatingBar from "@/components/RatingBar";
import RatingForm from "@/components/RatingForm";

export default function ServicePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [service, setService] = useState<Service | null>(null);
  const [ratings, setRatings] = useState<RatingAggregated | null>(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    getService(id).then(setService);
    getRatings(id).then(setRatings);
  }, [id]);

  const handleRate = async (payload: Parameters<typeof submitRating>[1]) => {
    await submitRating(id, payload);
    const updated = await getRatings(id);
    setRatings(updated);
    setSubmitted(true);
  };

  if (!service) return <div className="min-h-screen bg-gray-950 text-gray-400 flex items-center justify-center text-sm">Loading...</div>;

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100">
      <div className="border-b border-gray-800 px-6 py-5">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <button onClick={() => router.back()} className="text-sm text-gray-500 hover:text-gray-300 transition">
            ← Back
          </button>
          <h1 className="text-lg font-bold">nAIm</h1>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-8 space-y-8">
        {/* Service header */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">{service.category_slug}</span>
            {service.verified && <span className="text-xs bg-green-900/40 text-green-400 px-2 py-0.5 rounded-full">verified</span>}
          </div>
          <h2 className="text-2xl font-bold">{service.name}</h2>
          <p className="text-gray-500 text-sm mt-1">{service.canonical_provider}</p>
          <p className="text-gray-300 mt-3">{service.description}</p>
        </div>

        {/* Details */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500 text-xs mb-1">Pricing</p>
            <p className="text-white capitalize">{service.pricing_model.replace("_", " ")}</p>
            {service.pricing_notes && <p className="text-gray-400 text-xs mt-1">{service.pricing_notes}</p>}
          </div>
          <div>
            <p className="text-gray-500 text-xs mb-1">Auth</p>
            <p className="text-white capitalize">{service.auth_type.replace("_", " ")}</p>
          </div>
          <div>
            <p className="text-gray-500 text-xs mb-1">Base URL</p>
            <p className="text-gray-300 text-xs break-all">{service.base_url}</p>
          </div>
          <div>
            <p className="text-gray-500 text-xs mb-1">Docs</p>
            <a href={service.docs_url} target="_blank" className="text-blue-400 text-xs hover:underline break-all">
              {service.docs_url}
            </a>
          </div>
        </div>

        {/* Ratings */}
        {ratings && ratings.count > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Agent Ratings</h3>
              <span className="text-xs text-gray-500">{ratings.count} rating{ratings.count !== 1 ? "s" : ""}</span>
            </div>
            <div className="space-y-3">
              <RatingBar label="Overall" value={ratings.avg_overall} />
              <RatingBar label="Quality" value={ratings.avg_quality} />
              <RatingBar label="Latency" value={ratings.avg_latency} />
              <RatingBar label="Reliability" value={ratings.avg_reliability} />
              <RatingBar label="Cost" value={ratings.avg_cost} />
            </div>
          </div>
        )}

        {/* Rating form */}
        {!submitted ? (
          <RatingForm onSubmit={handleRate} />
        ) : (
          <p className="text-green-400 text-sm">Rating submitted. Thank you.</p>
        )}
      </div>
    </main>
  );
}
