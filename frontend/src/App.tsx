import { useEffect, useState } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { Users, Search, TrendingUp, ExternalLink } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- Utility ---
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- Types ---
interface Influencer {
  username: string;
  platform: string;
  followers: number;
  engagement_rate: number;
  conversion_potential: number;
  sales_language_score: number;
  influence_score: number;
  has_whatsapp: boolean;
  link_in_bio: string;
  calculated_ranking_score?: number; // Added optional property
}

// --- Components ---

const StatCard = ({ label, value, icon: Icon, color }: any) => (
  <div className="bg-slate-800/50 backdrop-blur-md p-6 rounded-xl border border-slate-700">
    <div className="flex items-center justify-between mb-2">
      <span className="text-slate-400 text-sm font-medium">{label}</span>
      <Icon className={cn("w-5 h-5", color)} />
    </div>
    <div className="text-2xl font-bold text-white">{value}</div>
  </div>
);

export default function App() {
  const [influencers, setInfluencers] = useState<Influencer[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchInfluencers = async () => {
    try {
      const res = await fetch('http://localhost:8001/influencers');
      const data = await res.json();
      setInfluencers(data);
    } catch (e) {
      console.error(e);
    }
  };

  const triggerCollection = async () => {
    setLoading(true);
    try {
      await fetch('http://localhost:8001/collect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platforms: ['instagram'], limit: 5 })
      });
      await fetchInfluencers();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInfluencers();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <header className="max-w-7xl mx-auto mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            Protocolo Horus
          </h1>
          <p className="text-slate-400 mt-2">Radar de Afiliados Locais</p>
        </div>
        <button
          onClick={triggerCollection}
          disabled={loading}
          className="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all disabled:opacity-50"
        >
          {loading ? 'Calculando...' : <><Search className="w-5 h-5" /> Escanear Rede</>}
        </button>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Left Col: Stats & Radar */}
        <div className="lg:col-span-1 space-y-8">
          <div className="grid grid-cols-2 gap-4">
            <StatCard label="Perfis Rastreados" value={influencers.length} icon={Users} color="text-blue-400" />
            <StatCard label="Média Afiliados" value={`${(influencers.reduce((acc, i) => acc + i.influence_score, 0) / (influencers.length || 1)).toFixed(1)}`} icon={TrendingUp} color="text-emerald-400" />
          </div>

          <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700 h-[400px]">
            <h3 className="text-lg font-semibold mb-4">Métricas de Conversão (Médias)</h3>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                { subject: 'Engajamento', A: 80, fullMark: 100 },
                { subject: 'Vendas', A: 65, fullMark: 100 },
                { subject: 'Links', A: 90, fullMark: 100 },
                { subject: 'Autenticidade', A: 70, fullMark: 100 },
                { subject: 'Crescimento', A: 50, fullMark: 100 },
              ]}>
                <PolarGrid stroke="#475569" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8' }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name="Média" dataKey="A" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Col: Ranking List */}
        <div className="lg:col-span-2">
          <div className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
            <div className="p-6 border-b border-slate-700">
              <h2 className="text-xl font-bold">Top Afiliados Potenciais</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-800 text-slate-400 uppercase text-xs">
                  <tr>
                    <th className="px-6 py-4">Influencer</th>
                    <th className="px-6 py-4">Plataforma</th>
                    <th className="px-6 py-4 text-center">Whatsapp</th>
                    <th className="px-6 py-4 text-center">Score Venda</th>
                    <th className="px-6 py-4 text-right">Potencial Geral</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {influencers.map((inf, idx) => (
                    <tr key={idx} className="hover:bg-slate-700/30 transition-colors">
                      <td className="px-6 py-4 font-medium text-white flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center text-xs">
                          {inf.username[0].toUpperCase()}
                        </div>
                        <div className="flex flex-col">
                          <span>{inf.username}</span>
                          <a
                            href={inf.platform === 'instagram' ? `https://instagram.com/${inf.username}` : `https://tiktok.com/@${inf.username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                          >
                            Ver Perfil <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-300 capitalize">{inf.platform}</td>
                      <td className="px-6 py-4 text-center">
                        {inf.has_whatsapp ?
                          <span className="inline-block w-3 h-3 bg-green-500 rounded-full shadow-[0_0_10px_rgba(34,197,94,0.5)]"></span> :
                          <span className="inline-block w-3 h-3 bg-slate-600 rounded-full"></span>
                        }
                      </td>
                      <td className="px-6 py-4 text-center text-emerald-400 font-bold">
                        {inf.sales_language_score.toFixed(0)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <span className="text-lg font-bold text-white">{inf.calculated_ranking_score?.toFixed(1) || inf.influence_score.toFixed(1)}</span>
                          <TrendingUp className="w-4 h-4 text-emerald-500" />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
