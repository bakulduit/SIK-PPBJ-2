import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Loader2, X } from "lucide-react";
import api, { rupiah } from "@/lib/api";

const TYPE_STYLE = {
  PPBJ: "bg-teal-50 text-teal-700 border-teal-200",
  PUM: "bg-amber-50 text-amber-700 border-amber-200",
  PP: "bg-indigo-50 text-indigo-700 border-indigo-200",
  PTUM: "bg-purple-50 text-purple-700 border-purple-200",
  KASKECIL: "bg-emerald-50 text-emerald-700 border-emerald-200",
  NRP: "bg-slate-100 text-slate-700 border-slate-200",
};

const STATUS_LABEL = {
  draft: "Draft",
  pending_approval: "Menunggu",
  approved: "Disetujui",
  rejected: "Ditolak",
  posted: "Dijurnal",
};

export default function GlobalSearch() {
  const nav = useNavigate();
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const boxRef = useRef(null);
  const inputRef = useRef(null);
  const timer = useRef(null);

  // Debounced search
  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    const term = q.trim();
    if (term.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    timer.current = setTimeout(async () => {
      try {
        const r = await api.get(`/documents/search`, { params: { q: term } });
        setResults(Array.isArray(r.data) ? r.data : []);
        setOpen(true);
        setActive(-1);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [q]);

  // Close on outside click
  useEffect(() => {
    const onClick = (e) => {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const goTo = useCallback((doc) => {
    setOpen(false);
    setQ("");
    setResults([]);
    nav(`/documents/${doc.id}`);
  }, [nav]);

  const onKeyDown = (e) => {
    if (!open || results.length === 0) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setActive((a) => Math.min(a + 1, results.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === "Enter" && active >= 0) { e.preventDefault(); goTo(results[active]); }
    else if (e.key === "Escape") { setOpen(false); }
  };

  const term = q.trim();

  return (
    <div ref={boxRef} className="relative w-full max-w-md" data-testid="global-search">
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          ref={inputRef}
          data-testid="global-search-input"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onFocus={() => { if (results.length) setOpen(true); }}
          onKeyDown={onKeyDown}
          placeholder="Cari dokumen: nomor, kegiatan, supplier…"
          className="w-full pl-9 pr-9 py-2 rounded-lg border border-slate-300 bg-slate-50 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#14758a]/30 focus:border-[#14758a] focus:bg-white transition-colors"
        />
        {loading && <Loader2 className="w-4 h-4 text-[#14758a] absolute right-3 top-1/2 -translate-y-1/2 animate-spin" />}
        {!loading && q && (
          <button type="button" onClick={() => { setQ(""); setResults([]); inputRef.current?.focus(); }}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 rounded text-slate-400 hover:text-slate-600" aria-label="Bersihkan">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {open && term.length >= 2 && (
        <div data-testid="global-search-results"
          className="absolute z-50 mt-2 w-full bg-white border border-slate-200 rounded-xl shadow-lg overflow-hidden animate-fade-in">
          {loading && results.length === 0 && (
            <div className="px-4 py-6 text-center text-sm text-slate-400">Mencari…</div>
          )}
          {!loading && results.length === 0 && (
            <div className="px-4 py-6 text-center text-sm text-slate-400">
              Tidak ada dokumen cocok dengan “{term}”.
            </div>
          )}
          {results.length > 0 && (
            <div className="max-h-[70vh] overflow-y-auto thin-scroll py-1">
              <div className="px-4 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                {results.length} dokumen ditemukan
              </div>
              {results.map((d, i) => (
                <button key={d.id} type="button" onClick={() => goTo(d)}
                  onMouseEnter={() => setActive(i)}
                  data-testid={`search-result-${i}`}
                  className={`w-full flex items-start gap-3 px-4 py-2.5 text-left transition-colors ${active === i ? "bg-teal-50" : "hover:bg-slate-50"}`}>
                  <span className={`inline-flex items-center justify-center px-2 py-0.5 rounded border text-[11px] font-bold shrink-0 mt-0.5 ${TYPE_STYLE[d.doc_type] || "bg-slate-100 text-slate-700 border-slate-200"}`}>
                    {d.doc_type}
                  </span>
                  <span className="flex-1 min-w-0">
                    <span className="flex items-center gap-2">
                      <span className="font-mono text-xs text-slate-500 truncate">{d.no}</span>
                      {d.status && (
                        <span className="text-[10px] font-semibold text-slate-400">• {STATUS_LABEL[d.status] || d.status}</span>
                      )}
                    </span>
                    <span className="block text-sm font-semibold text-slate-800 truncate">
                      {d.kegiatan || d.keterangan || d.supplier || "(Tanpa keterangan)"}
                    </span>
                    <span className="block text-xs text-slate-500 truncate">
                      {[d.unit_kerja, d.supplier].filter(Boolean).join(" · ")}
                    </span>
                  </span>
                  <span className="text-xs font-semibold text-slate-700 tabular shrink-0 mt-0.5">{rupiah(d.total)}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
