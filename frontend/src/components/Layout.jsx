import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Landmark, Calculator, FileText, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Ledger<span>Relief</span></div>
        <div className="brand-sub">Debt Recovery Console</div>

        <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
          <LayoutDashboard size={17} /> Dashboard
        </NavLink>
        <NavLink to="/loans" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
          <Landmark size={17} /> Loans
        </NavLink>
        <NavLink to="/predictor" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
          <Calculator size={17} /> Settlement Predictor
        </NavLink>
        <NavLink to="/letters" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
          <FileText size={17} /> Letter Generator
        </NavLink>

        <div className="sidebar-footer">
          <div>{user?.full_name}</div>
          <div className="mono" style={{ fontSize: "0.75rem", opacity: 0.7 }}>{user?.email}</div>
          <button className="logout-btn" onClick={logout}>
            <LogOut size={14} style={{ marginRight: 6 }} />
            Sign out
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
