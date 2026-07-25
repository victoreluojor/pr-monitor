"use client";

type Mention = {
  id: string;
  title: string | null;
  source_type: string;
  source_name: string | null;
  url: string;
  sentiment_label: string;
  fetched_at: string;
};

const SENTIMENT_STYLES: Record<string, string> = {
  positive: "bg-green-100 text-green-800",
  negative: "bg-red-100 text-red-800",
  neutral: "bg-gray-100 text-gray-700",
  unscored: "bg-gray-50 text-gray-400",
};

export default function MentionFeed({ mentions }: { mentions: Mention[] }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-sm font-medium mb-3">Live mention feed</h3>
      <div className="space-y-2 max-h-[420px] overflow-y-auto">
        {mentions.length === 0 && (
          <p className="text-sm text-gray-400">No mentions yet — the ingestion worker checks this client every few hours.</p>
        )}
        {mentions.map((m) => (
          <a
            key={m.id}
            href={m.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block border-b last:border-0 pb-2 hover:bg-gray-50 rounded px-1"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-medium truncate">{m.title || m.url}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${SENTIMENT_STYLES[m.sentiment_label]}`}>
                {m.sentiment_label}
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-0.5">
              {m.source_type} · {m.source_name} · {new Date(m.fetched_at).toLocaleString()}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
