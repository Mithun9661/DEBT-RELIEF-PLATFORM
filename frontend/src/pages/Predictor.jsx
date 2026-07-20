import { useEffect, useState } from "react";
import { listLoans, predictSettlement, getNegotiationStrategy } from "../api";

const money = (n) => `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export default function Predictor() {
  const [loans, setLoans] = useState([]);
  const [selectedLoanId, setSelectedLoanId] = useState("");
  const [lumpSum, setLumpSum] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [strategy, setStrategy] = useState("");
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [loadingStrategy, setLoadingStrategy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      const { data } = await listLoans();
      setLoans(data);
      if (data.length) setSelectedLoanId(String(data[0].id));
    })();
  }, []);

  const selectedLoan = loans.find((l) => String(l.id) === selectedLoanId);

  const runPrediction = async (e) => {
    e.preventDefault();
    setError("");
    setPrediction(null);
    setStrategy("");
    setLoadingPrediction(true);
    try {
      const { data } = await predictSettlement({
        loan_id: parseInt(selectedLoanId),
        lump_sum_available: lumpSum ? parseFloat(lumpSum) : null,
      });
      setPrediction(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not generate a prediction.");
    } finally {
      setLoadingPrediction(false);
    }
  };

  const runStrategy = async () => {
    setLoadingStrategy(true);
    setError("");
    try {
      const { data } = await getNegotiationStrategy(parseInt(selectedLoanId));
      setStrategy(data.strategy);
    } catch (err) {
      setError(err.response?.data?.detail || "AI strategy is unavailable right now.");
    } finally {
      setLoadingStrategy(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="page-eyebrow">Projection Worksheet</span>
          <h1>Settlement Predictor</h1>
        </div>
      </div>

      {loans.length === 0 ? (
        <div className="panel">
          <div className="empty-state">
            <h3>No accounts to analyze</h3>
            <p>Add a loan on the Loans page first, then come back to run a prediction.</p>
          </div>
        </div>
      ) : (
        <div className="grid-2">
          <div className="panel">
            <div className="panel-title">Run a Prediction</div>
            {error && <div className="error-box">{error}</div>}
            <form onSubmit={runPrediction}>
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
                <label>Lump sum available (optional, $)</label>
                <input
                  type="number" min="0" step="0.01"
                  value={lumpSum}
                  onChange={(e) => setLumpSum(e.target.value)}
                  placeholder="e.g. 3000"
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={loadingPrediction}>
                {loadingPrediction ? "Calculating…" : "Predict settlement"}
              </button>
            </form>

            {prediction && (
              <div style={{ marginTop: 24, borderTop: "1px solid var(--line)", paddingTop: 20 }}>
                <div className="ledger-row">
                  <span className="label">Predicted settlement</span>
                  <span className="value gold">{(prediction.predicted_settlement_pct * 100).toFixed(1)}% of balance</span>
                </div>
                <div className="ledger-row">
                  <span className="label">Estimated amount</span>
                  <span className="value positive">{money(prediction.predicted_settlement_amount)}</span>
                </div>
                <div className="ledger-row">
                  <span className="label">Model confidence</span>
                  <span className="value">{(prediction.confidence_score * 100).toFixed(0)}%</span>
                </div>
                <p style={{ fontSize: "0.88rem", color: "var(--parchment-dim)", marginTop: 12 }}>
                  {prediction.strategy_summary}
                </p>
              </div>
            )}
          </div>

          <div className="panel">
            <div className="panel-title">AI Negotiation Strategy</div>
            <p style={{ fontSize: "0.88rem", color: "var(--parchment-dim)", marginBottom: 16 }}>
              Generate a Gemini-powered talking-points strategy for {selectedLoan?.creditor_name || "this account"},
              grounded in the numbers above.
            </p>
            <button className="btn btn-secondary" onClick={runStrategy} disabled={loadingStrategy || !selectedLoanId}>
              {loadingStrategy ? "Thinking…" : "Generate strategy"}
            </button>
            {strategy && (
              <div className="letter-output" style={{ marginTop: 18 }}>
                {strategy}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
