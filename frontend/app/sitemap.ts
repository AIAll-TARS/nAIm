import { MetadataRoute } from "next";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://api.naim.janis7ewski.org";
const BASE_URL = "https://naim.janis7ewski.org";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  let services: { id: string; updated_at: string }[] = [];

  try {
    const res = await fetch(`${API_URL}/v1/services?limit=500`, {
      next: { revalidate: 86400 },
    });
    if (res.ok) {
      services = await res.json();
    }
  } catch {
    // if API is unreachable at build time, just return the root
  }

  const servicePages: MetadataRoute.Sitemap = services.map((s) => ({
    url: `${BASE_URL}/services/${s.id}`,
    lastModified: new Date(s.updated_at),
    changeFrequency: "weekly",
    priority: 0.7,
  }));

  return [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    ...servicePages,
  ];
}
