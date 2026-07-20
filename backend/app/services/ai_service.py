"""
Google Gemini integration.

This module isolates all calls to the Gemini API so the rest of the app
never talks to the SDK directly. It degrades gracefully to a clear error
message if no API key is configured, rather than crashing the request.
"""
import logging

import google.generativeai as genai

from app.core.config import get_settings
from app.models import Loan

logger = logging.getLogger("ai_service")
settings = get_settings()

_configured = False


def _ensure_configured():
    global _configured
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to backend/.env to enable AI features."
        )
    if not _configured:
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


def _get_model():
    _ensure_configured()
    return genai.GenerativeModel(settings.gemini_model)


def generate_negotiation_strategy(
    loan: Loan,
    financial_summary: dict,
    predicted_settlement: dict,
) -> str:
    """
    Ask Gemini for a short, borrower-facing negotiation strategy paragraph,
    grounded in the numbers already computed deterministically.
    """
    model = _get_model()

    prompt = f"""You are a financial counselor assistant helping a borrower prepare to
negotiate a debt settlement. Do not invent numbers; use only the figures given.

Debt details:
- Creditor: {loan.creditor_name}
- Loan type: {loan.loan_type.value}
- Current balance: ${loan.current_balance:,.2f}
- Status: {loan.status.value}
- Months delinquent: {loan.months_delinquent}

Borrower financial snapshot:
- Debt-to-income ratio: {financial_summary['debt_to_income_ratio']:.0%}
- Disposable income/month: ${financial_summary['disposable_income']:,.2f}
- Financial health: {financial_summary['health_label']}

Model-estimated settlement target:
- Suggested settlement: {predicted_settlement['predicted_settlement_pct']:.0%} of balance
  (~${predicted_settlement['predicted_settlement_amount']:,.2f})

Write a concise (120-180 word) negotiation strategy the borrower can follow when
calling or emailing the creditor. Cover: opening offer, walk-away point, useful
leverage points given their situation, and one practical tip about getting any
agreement in writing. Plain language, no legal advice disclaimers needed beyond
one short sentence at the end recommending they consult a licensed credit
counselor for their specific situation."""

    response = model.generate_content(prompt)
    return response.text.strip()


def generate_negotiation_letter(
    loan: Loan,
    tone: str,
    offer_amount: float | None,
    hardship_reason: str | None,
    borrower_name: str,
) -> str:
    """Ask Gemini to draft a full settlement negotiation letter."""
    model = _get_model()

    offer_line = (
        f"The borrower would like to propose a lump-sum settlement offer of "
        f"${offer_amount:,.2f}." if offer_amount else
        "The borrower has not decided on a specific offer amount yet; "
        "propose a reasonable one based on typical settlement ranges for this debt type."
    )
    hardship_line = f"Hardship context to reference: {hardship_reason}." if hardship_reason else ""

    prompt = f"""Draft a formal debt settlement negotiation letter from a borrower to a
creditor/collections agency. Tone should be {tone}.

Borrower name: {borrower_name}
Creditor: {loan.creditor_name}
Account type: {loan.loan_type.value}
Current balance: ${loan.current_balance:,.2f}
Account status: {loan.status.value}

{offer_line}
{hardship_line}

Requirements:
- Professional business-letter format (no placeholder brackets like [Date] left unresolved;
  instead write "the date of this letter" or similar natural phrasing)
- Reference the account balance and status
- Make a clear settlement proposal with a request for written confirmation
- State the offer is conditional on written agreement before payment
- Keep it under 300 words
- Sign off with the borrower's name only, no fabricated contact details

Return only the letter text, no preamble or explanation."""

    response = model.generate_content(prompt)
    return response.text.strip()
