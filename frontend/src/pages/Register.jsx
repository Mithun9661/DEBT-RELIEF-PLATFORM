import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    monthly_income: "",
    monthly_expenses: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        monthly_income: parseFloat(form.monthly_income) || 0,
        monthly_expenses: parseFloat(form.monthly_expenses) || 0,
      });
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to create your account.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card" style={{ width: 440 }}>
        <h1>Create your account</h1>
        <p className="auth-sub">Start tracking debt and building a recovery plan.</p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Full name</label>
            <input required value={form.full_name} onChange={update("full_name")} placeholder="Jordan Rivera" />
          </div>
          <div className="field">
            <label>Email</label>
            <input type="email" required value={form.email} onChange={update("email")} placeholder="you@example.com" />
          </div>
          <div className="field">
            <label>Password</label>
            <input type="password" required minLength={8} value={form.password} onChange={update("password")} placeholder="At least 8 characters" />
          </div>
          <div className="field-row">
            <div className="field">
              <label>Monthly income ($)</label>
              <input type="number" min="0" step="0.01" value={form.monthly_income} onChange={update("monthly_income")} placeholder="5000" />
            </div>
            <div className="field">
              <label>Monthly expenses ($)</label>
              <input type="number" min="0" step="0.01" value={form.monthly_expenses} onChange={update("monthly_expenses")} placeholder="2000" />
            </div>
          </div>
          <button className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }} disabled={busy} type="submit">
            {busy ? "Creating account…" : "Create account"}
          </button>
        </form>

        <div className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
