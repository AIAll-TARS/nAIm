import { Metadata } from "next";
import ServicePageClient from "./ServicePageClient";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://api.naim.janis7ewski.org";

async function fetchService(id: string) {
  try {
    const res = await fetch(`${API_URL}/v1/services/${id}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const service = await fetchService(id);

  if (!service) {
    return { title: "Service — nAIm" };
  }

  const title = `${service.name} — nAIm`;
  const description = `${service.description} | Category: ${service.category_slug} | Auth: ${service.auth_type} | Pricing: ${service.pricing_model}`;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `https://naim.janis7ewski.org/services/${id}`,
      siteName: "nAIm",
      type: "website",
    },
    twitter: {
      card: "summary",
      title,
      description,
    },
  };
}

export default async function ServicePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ServicePageClient id={id} />;
}
