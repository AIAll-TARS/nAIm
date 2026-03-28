"use client";
import { useState, useEffect } from "react";
import { pingPresence, Service, Category } from "@/lib/api";
import ServiceCard from "@/components/ServiceCard";

interface Props {
  initialServices: Service[];
  categories: Category[];
}

export default function ServiceBrowser({ initialServices, categories }: Props) {
  const [activeCategory, setActiveCategory] = useState<string | undefined>();
  const [search, setSearch] = useState("");
  const [services, setServices] = useState<Service[]>(initialServices);
  const [loading, setLoading] = useState(false);
  const [activeVisitors, setActiveVisitors] = useState<number | null>(null);

  useEffect(() => {
    pingPresence().then(setActiveVisitors).catch(() => {});
    const interval = setInterval(() => {
      pingPresence().then(setActiveVisitors).catch(() => {});
    }, 60_000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeCategory === undefined) {
      setServices(initialServices);
      return;
    }
    setLoading(true);
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "https://api.naim.janis7ewski.org"}/v1/services?category=${activeCategory}`
    )
      .then((r) => r.json())
      .then((data) => setServices(data))
      .finally(() => setLoading(false));
  }, [activeCategory, initialServices]);

  const filtered = services.filter(
    (s) =>
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.canonical_provider.toLowerCase().includes(search.toLowerCase()) ||
      s.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      {/* Header bar with visitor count */}
      <div className="border-b border-gray-800 px-6 py-5">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">nAIm</h1>
            <p className="text-sm text-gray-400 mt-0.5">API service registry for AI agents</p>
          </div>
          <div className="flex items-center gap-4">
            {activeVisitors !== null && (
              <span className="text-xs text-gray-500 flex items-center gap-1.5">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                {activeVisitors} browsing now
              </span>
            )}
            <a
              href="https://github.com/AIAll-TARS/nAIm"
              target="_blank"
              className="text-xs text-gray-500 hover:text-gray-300 transition"
            >
              GitHub
            </a>
          </div>
        </div>
      </div>

      {/* Search + filter */}
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
                activeCategory === cat.slug
                  ? "bg-white text-gray-900"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
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
    </>
  );
}
