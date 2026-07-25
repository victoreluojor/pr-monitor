"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

const COLORS: Record<string, string> = {
  positive: "#4caf7d",
  negative: "#d9534f",
  neutral: "#9e9e9e",
  unscored: "#d0d0d0",
};

export default function SentimentChart({ breakdown }: { breakdown: Record<string, number> }) {
  const data = Object.entries(breakdown).map(([name, value]) => ({ name, value }));

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-sm font-medium mb-2">Sentiment breakdown</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || "#ccc"} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
