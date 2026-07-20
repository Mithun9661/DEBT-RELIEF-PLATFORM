import { useEffect, useState } from "react";
import { Plus, Trash2, X } from "lucide-react";
import { listLoans, createLoan, deleteLoan } from "../api";

const LOAN_TYPES = ["credit_card", "personal_loan", "medical_debt", "student_loan", "auto_loan", "mortgage", "other"];
const STATUSES = ["active", "delinquent", "in_collections", "settled", "paid_off"];

const money = (n) => `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const emptyForm = {
  creditor_name: "",
  loan_type: "credit_card",
  original_balance: "",
  current_balance: "",
  interest_rate: "",
  minimum_payment: "",
  status: "active",
  months_delinquent: 0,
};

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    const { data } = await listLoans();
    setLoans(data);
  };

  useEffect(() => {
    (async () => {
      await refresh();
      setLoading(false);
    })();
  }, []);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await createLoan({
        ...form,
        original_balance: parseFloat(form.original_balance),
        current_balance: parseFloat(form.current_balance),
        interest_rate: parseFloat(form.interest_rate) || 0,
        minimum_payment: parseFloat(form.minimum_payment) || 0,
        months_delinquent: parseInt(form.months_delinquent) || 0,
      });
      setForm(emptyForm);
      setShowForm(false);
      await refresh();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save this account.");
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async (id) => {
    await deleteLoan(id);
    await refresh();
  };

  if (loading) return <p className="spinner-text">Loading accounts…</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="page-eyebrow">Debt Register</span>
          <h1>Loans &amp; Credit Accounts</h1>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? <X size={16} /> : <Plus size={16} />}
          {showForm ? "Cancel" : "Add account"}
        </button>
      </div>

      {showForm && (
        <div className="panel" style={{ marginBottom: 24 }}>
          <div className="panel-title">New Account</div>
          {error && <div className="error-box">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Creditor name</label>
              <input required value={form.creditor_name} onChange={update("creditor_name")} placeholder="Capital One" />
            </div>
            <div className="field-row">
              <div className="field">
                <label>Loan type</label>
                <select value={form.loan_type} onChange={update("loan_type")}>
                  {LOAN_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Status</label>
                <select value={form.status} onChange={update("status")}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
                </select>
              </div>
            </div>
            <div className="field-row">
              <div className="field">
                <label>Original balance ($)</label>
                <input type="number" step="0.01" min="0.01" required value={form.original_balance} onChange={update("original_balance")} />
              </div>
              <div className="field">
                <label>Current balance ($)</label>
                <input type="number" step="0.01" min="0" required value={form.current_balance} onChange={update("current_balance")} />
              </div>
            </div>
            <div className="field-row">
              <div className="field">
                <label>Interest rate (% APR)</label>
                <input type="number" step="0.01" min="0" value={form.interest_rate} onChange={update("interest_rate")} />
              </div>
              <div className="field">
                <label>Minimum payment ($/mo)</label>
                <input type="number" step="0.01" min="0" value={form.minimum_payment} onChange={update("minimum_payment")} />
              </div>
            </div>
            <div className="field">
              <label>Months delinquent</label>
              <input type="number" step="1" min="0" value={form.months_delinquent} onChange={update("months_delinquent")} />
            </div>
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? "Saving…" : "Save account"}
            </button>
          </form>
        </div>
      )}

      <div className="panel">
        <div className="panel-title">All Accounts ({loans.length})</div>
        {loans.length === 0 ? (
          <div className="empty-state">
            <h3>No accounts yet</h3>
            <p>Add your first loan or credit account above.</p>
          </div>
        ) : (
          loans.map((loan) => (
            <div className="loan-card" key={loan.id}>
              <div>
                <div className="loan-name">{loan.creditor_name}</div>
                <div className="loan-meta">
                  {loan.loan_type.replace("_", " ")} · {loan.interest_rate}% APR · min. {money(loan.minimum_payment)}/mo
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ textAlign: "right" }}>
                  <div className="mono" style={{ fontSize: "1.05rem" }}>{money(loan.current_balance)}</div>
                  <span className={`status-pill ${loan.status}`}>{loan.status.replace("_", " ")}</span>
                </div>
                <button
                  className="btn btn-secondary"
                  style={{ padding: 8 }}
                  onClick={() => handleDelete(loan.id)}
                  aria-label={`Delete ${loan.creditor_name}`}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
