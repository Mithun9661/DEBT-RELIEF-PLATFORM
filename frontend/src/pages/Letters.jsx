import { useEffect, useState } from "react";
import { listLoans, generateLetter } from "../api";

const TONES = [
  { value: "professional", label: "Professional" },
  { value: "firm", label: "Firm" },
  { value: "empathetic", label: "Empathetic" },
];

const money = (n) => `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function Letters() {
  const [loans, setLoans] = useState([]);
  const [selectedLoanId, setSelectedLoanId] = useState("");
  const [tone, setTone] = useState("professional");
  const [offerAmount, setOfferAmount] = useState("");
  const [hardshipReason, setHardshipReason] = useState("");
  const [letter, setLetter] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      const { data } = await listLoans();
      setLoans(data);
      if (data.length) setSelectedLoanId(String(data[0].id));
    })();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError("");
    setLetter("");
    setBusy(true);
    try {
      const { data } = await generateLetter({
        loan_id: parseInt(selectedLoanId),
        tone,
        offer_amount: offerAmount ? parseFloat(offerAmount) : null,
        hardship_reason: hardshipReason || null,
      });
      setLetter(data.letter);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not generate the letter.");
    } finally {
      setBusy(false);
    }
  };

  const handleCopy = () => navigator.clipboard.writeText(letter);

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="page-eyebrow">Correspondence Desk</span>
          <h1>AI Letter Generator</h1>
        </div>
      </div>

      {loans.length === 0 ? (
        <div className="panel">
          <div className="empty-state">
            <h3>No accounts to write about</h3>
            <p>Add a loan on the Loans page first.</p>
          </div>
        </div>
      ) : (
        <div className="grid-2">
          <div className="panel">
            <div className="panel-title">Letter Details</div>
            {error && <div className="error-box">{error}</div>}
            <form onSubmit={handleGenerate}>
              <div className="field">
                <label>Account</label>
                <select value={selectedLoanId} onChange={(e) => setSelectedLoanId(e.target.value)}>
                  {loans.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.creditor_name} — {money(l.current_balance)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label>Tone</label>
                <div className="tag-select">
                  {TONES.map((t) => (
                    <button
                      type="button"
                      key={t.value}
                      className={`tag-option${tone === t.value ? " selected" : ""}`}
                      onClick={() => setTone(t.value)}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="field">
                <label>Settlement offer (optional, $)</label>
                <input type="number" min="0" step="0.01" value={offerAmount} onChange={(e) => setOfferAmount(e.target.value)} placeholder="e.g. 2500" />
              </div>

              <div className="field">
                <label>Hardship reason (optional)</label>
                <textarea rows={3} value={hardshipReason} onChange={(e) => setHardshipReason(e.target.value)} placeholder="e.g. job loss, medical emergency" />
              </div>

              <button className="btn btn-primary" type="submit" disabled={busy || !selectedLoanId}>
                {busy ? "Drafting…" : "Generate letter"}
              </button>
            </form>
          </div>

          <div className="panel">
            <div className="panel-title" style={{ justifyContent: "space-between" }}>
              <span>Draft Letter</span>
              {letter && <button className="btn btn-secondary" onClick={handleCopy}>Copy</button>}
            </div>
            {letter ? (
              <div className="letter-output">{letter}</div>
            ) : (
              <p className="spinner-text">Your generated letter will appear here.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
