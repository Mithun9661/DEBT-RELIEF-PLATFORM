import client from "./client";

// ---- Auth ----
export const registerUser = (data) => client.post("/api/auth/register", data);

export const loginUser = (email, password) => {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  return client.post("/api/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

// ---- Users ----
export const getMyProfile = () => client.get("/api/users/me");
export const updateMyProfile = (data) => client.patch("/api/users/me", data);

// ---- Loans ----
export const listLoans = () => client.get("/api/loans");
export const createLoan = (data) => client.post("/api/loans", data);
export const updateLoan = (id, data) => client.patch(`/api/loans/${id}`, data);
export const deleteLoan = (id) => client.delete(`/api/loans/${id}`);

// ---- Financial Analysis ----
export const getFinancialHealth = () => client.get("/api/financial/health");
export const getNegotiationStrategy = (loanId) =>
  client.get(`/api/financial/strategy/${loanId}`);

// ---- Settlement Prediction ----
export const predictSettlement = (data) => client.post("/api/settlement/predict", data);
export const getSettlementHistory = () => client.get("/api/settlement/history");

// ---- AI Letters ----
export const generateLetter = (data) => client.post("/api/letters/generate", data);
export const getLetterHistory = () => client.get("/api/letters/history");
