import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:18792",
});

export interface Category {
  slug: string;
  label: string;
}

export interface Service {
  id: string;
  slug: string;
  name: string;
  canonical_provider: string;
  category_slug: string;
  description: string;
  docs_url: string;
  base_url: string;
  auth_type: string;
  pricing_model: string;
  pricing_notes: string | null;
  status: string;
  verified: boolean;
  avg_rating: number | null;
  rating_count: number;
  created_at: string;
  updated_at: string;
}

export interface RatingAggregated {
  service_id: string;
  count: number;
  avg_cost: number;
  avg_quality: number;
  avg_latency: number;
  avg_reliability: number;
  avg_overall: number;
  updated_at: string | null;
}

export const getCategories = () =>
  api.get<Category[]>("/v1/categories").then((r) => r.data);

export const getServices = (category?: string) =>
  api.get<Service[]>("/v1/services", { params: category ? { category } : {} }).then((r) => r.data);

export const getService = (id: string) =>
  api.get<Service>(`/v1/services/${id}`).then((r) => r.data);

export const getRatings = (serviceId: string) =>
  api.get<RatingAggregated>(`/v1/services/${serviceId}/ratings`).then((r) => r.data);

export const submitRating = (serviceId: string, payload: {
  cost_score: number;
  quality_score: number;
  latency_score: number;
  reliability_score: number;
  agent_id?: string;
  notes?: string;
}) => api.post(`/v1/services/${serviceId}/ratings`, payload).then((r) => r.data);

export const pingPresence = () =>
  api.get<{ active: number }>("/v1/tools/presence").then((r) => r.data.active);
