import type { MetadataRoute } from "next";

type ServiceListItem = {
  id: string;
  updated_at?: string;
};

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://naim.janis7ewski.org";
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://api.naim.janis7ewski.org";

async function getServices(): Promise<ServiceListItem[]> {
  try {
    const response = await fetch(`${apiUrl}/v1/services?limit=1000`, {
      next: { revalidate: 3600 },
    });

    if (!response.ok) return [];

    const data = (await response.json()) as ServiceListItem[];
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const services = await getServices();

  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: siteUrl,
      lastModified: new Date(),
      changeFrequency: "hourly",
      priority: 1,
    },
  ];

  const serviceRoutes: MetadataRoute.Sitemap = services
    .filter((service) => typeof service.id === "string" && service.id.length > 0)
    .map((service) => ({
      url: `${siteUrl}/services/${service.id}`,
      lastModified: service.updated_at ? new Date(service.updated_at) : new Date(),
      changeFrequency: "daily" as const,
      priority: 0.8,
    }));

  return [...staticRoutes, ...serviceRoutes];
}
