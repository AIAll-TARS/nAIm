import ServiceBrowser from "@/components/ServiceBrowser";
import { Category, Service } from "@/lib/api";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://api.naim.janis7ewski.org";

async function getCategories(): Promise<Category[]> {
  try {
    const res = await fetch(`${API_URL}/v1/categories`, {
      next: { revalidate: 300 }, // cache 5 min
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

async function getServices(): Promise<Service[]> {
  try {
    const res = await fetch(`${API_URL}/v1/services`, {
      next: { revalidate: 300 }, // cache 5 min
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function Home() {
  const [categories, services] = await Promise.all([
    getCategories(),
    getServices(),
  ]);

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100">
      <ServiceBrowser initialServices={services} categories={categories} />
    </main>
  );
}
