"use client";
import { useEffect, useState } from "react";
import { getCategories, getServices, Service, Category } from "@/lib/api";
import ServiceCard from "@/components/ServiceCard";

export default function Home() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [activeCategory, setActiveCategory] = useState<string | undefined>();
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCategories().then(setCategories);
  }, []);

  useEffect(() => {
    setLoading(true);
    getServices(activeCategory)
      .then(setServices)
      .finally(() => setLoading(false));
  }, [activeCategory]);

  const filtered = services.filter(
    (s) =>
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.canonical_provider.toLowerCase().includes(search.toLowerCase()) ||
      s.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100">
      <div className="border-b border-gray-800 px-6 py-5">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">nAIm</h1>
            <p className="text-sm text-gray-400 mt-0.5">API service registry for AI agents</p>
          </div>
          <a
            href="https://github.com/AIAll-TARS/nAIm"
            target="_blank"
            className="text-xs text-gray-500 hover:text-gray-300 transition"
          >
            GitHub
          </a>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <input
          type="text"
          placeholder="Search services..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-sm placeholder-gray-500 focus:outline-none focus:border-gray-500 mb-6"
        />

        <div className="flex flex-wrap gap-2 mb-8">
          <button
            onClick={() => setActiveCategory(undefined)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition ${
              !activeCategory ? "bg-white text-gray-900" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat.slug}
              onClick={() => setActiveCategory(cat.slug)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition ${
                activeCategory === cat.slug ? "bg-white text-gray-900" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="text-gray-500 text-sm">Loading...</p>
        ) : filtered.length === 0 ? (
          <p className="text-gray-500 text-sm">No services found.</p>
        ) : (
          <div className="grid gap-4">
            {filtered.map((service) => (
              <ServiceCard key={service.id} service={service} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
