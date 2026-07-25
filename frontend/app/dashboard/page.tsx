"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, logout } from "@/lib/api";
import SentimentChart from "@/components/SentimentChart";
import VolumeChart from "@/components/VolumeChart";
import MentionFeed from "@/components/MentionFeed";

type Client = { id: string; name: string };

export default function DashboardPage() {
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [summary, setSummary] = useState<any>(null);
  const [mentions, setMentions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listClients()
      .then((data) => {
        setClients(data);
        if (data.length > 0) setSelectedClientId(data[0].id);
      })
      .catch(() => router.push("/"))
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (!selectedClientId) return;
    api.getDashboard(selectedClientId).then(setSummary).catch((e) => setError(e.message));
    api.listMentions(selectedClientId, "?limit=30").then(setMentions).catch((e) => setError(e.message));
  }, [selectedClientId]);

  if (loading) return <div className="p-8 text-sm text-gray-500">Loading...</div>;

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold">PR Media Monitor</h1>
        <div className="flex items-center gap-3">
          <select
            value={selectedClientId}
            onChange={(e) => setSelectedClientId(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm"
          >
            {clients.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <button
            onClick={() => { logout(); router.push("/"); }}
            className="text-sm text-gray-500 hover:text-gray-800"
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6 space-y-6">
        {error && <p className="text-sm text-red-600">{error}</p>}

        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-xs text-gray-400">Total mentions</p>
              <p className="text-2xl font-semibold">{summary.total_mentions}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-xs text-gray-400">Last 7 days</p>
              <p className="text-2xl font-semibold">{summary.mentions_last_7_days}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-xs text-gray-400">Top source</p>
              <p className="text-2xl font-semibold">
                {summary.top_sources[0]?.source || "—"}
              </p>
            </div>
          </div>
        )}

        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SentimentChart breakdown={summary.sentiment_breakdown} />
            <VolumeChart data={summary.volume_by_day} />
          </div>
        )}

        <MentionFeed mentions={mentions} />
      </main>
    </div>
  );
}
