import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { getFinancialHealth, listLoans } from "../api";
import { useAuth } from "../context/AuthContext";

const money = (n) => `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const pct = (n) => `${(n * 100).toFixed(1)}%`;

export default function Dashboard() {
  const { user } = useAuth();
  const [health, setHealth] = useState(null);
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [h, l] = await Promise.all([getFinancialHealth(), listLoans()]);
        setHealth(h.data);
        setLoans(l.data);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const today = new Date().toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });

  if (loading) return <p className="spinner-text">Loading your statement…</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <span className="page-eyebrow">Statement of Account</span>
          <h1>Good to see you, {user?.full_name?.split(" ")[0]}</h1>
        </div>
        <div className="page-date">{today}</div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="panel">
          <div className="panel-title">Financial Snapshot</div>
          <div className="ledger-row">
            <span className="label">Monthly income</span>
            <span className="value positive">{money(health.monthly_income)}</span>
          </div>
          <div className="ledger-row">
            <span className="label">Monthly expenses</span>
            <span className="value">{money(health.monthly_expenses)}</span>
          </div>
          <div className="ledger-row">
            <span className="label">Total minimum payments</span>
            <span className="value">{money(health.total_minimum_payments)}</span>
          </div>
          <div className="ledger-row">
            <span className="label">Disposable income / month</span>
            <span className={`value ${health.disposable_income >= 0 ? "positive" : "negative"}`}>
              {money(health.disposable_income)}
            </span>
          </div>
          <div className="ledger-row">
            <span className="label">Debt-to-income ratio</span>
            <span className="value gold">{pct(health.debt_to_income_ratio)}</span>
          </div>
          <div className="ledger-row">
            <span className="label">Total outstanding debt</span>
            <span className="value negative">{money(health.total_debt)}</span>
          </div>
        </div>

        <div className="panel" style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div className="panel-title" style={{ justifyContent: "center", textAlign: "center" }}>Financial Health</div>
          <div className="stamp">
            <div className="score">{health.financial_health_score}</div>
            <div className="label">{health.health_label}</div>
          </div>
          {health.risk_flags.length > 0 && (
            <div style={{ marginTop: 20 }}>
              {health.risk_flags.map((flag, i) => (
                <div className="risk-flag" key={i}>
                  <AlertTriangle size={15} style={{ flexShrink: 0, marginTop: 2 }} />
                  <span>{flag}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="panel">
        <div className="panel-title">Open Accounts ({loans.length})</div>
        {loans.length === 0 ? (
          <div className="empty-state">
            <h3>No debts on file yet</h3>
            <p>Add a loan or credit account to start building your recovery plan.</p>
          </div>
        ) : (
          loans.map((loan) => (
            <div className="loan-card" key={loan.id}>
              <div>
                <div className="loan-name">{loan.creditor_name}</div>
                <div className="loan-meta">{loan.loan_type.replace("_", " ")} · {loan.months_delinquent} mo. delinquent</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div className="mono" style={{ fontSize: "1.05rem" }}>{money(loan.current_balance)}</div>
                <span className={`status-pill ${loan.status}`}>{loan.status.replace("_", " ")}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
