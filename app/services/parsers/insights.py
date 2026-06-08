import os
from groq import Groq
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Transaction, Budget
from app.schemas import TransactionType

def gather_user_data(user_id, month, year, db: Session):

    current = db.query(Transaction.category, func.sum(Transaction.amount).label('Total')
                       ).filter(Transaction.user_id==user_id,
                                Transaction.type==TransactionType.DEBIT,
                                extract("month", Transaction.valueDate)==month,
                                extract("year", Transaction.valueDate)==year
                                ).group_by(Transaction.category).all()
    
    last_month = month-1 if month>1 else 12
    last_year = year if month>1 else year-1

    previous = db.query(Transaction.category, func.sum(Transaction.amount).label('Total')
                       ).filter(Transaction.user_id==user_id,
                                Transaction.type==TransactionType.DEBIT,
                                extract("month", Transaction.valueDate)==last_month,
                                extract("year", Transaction.valueDate)==last_year
                                ).group_by(Transaction.category).all()
    
    budgets = db.query(Budget).filter(Budget.user_id==user_id).all()

    large_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.DEBIT,
        func.extract("month", Transaction.valueDate) == month,
        func.extract("year", Transaction.valueDate) == year
        ).order_by(Transaction.amount.desc()).limit(5).all()

    return {
        "current": {r[0]: r[1] for r in current},
        "previous": {r[0]: r[1] for r in previous},
        "budgets": {b.category: b.monthly_limit for b in budgets},
        "large_txns": [
            {"amount": t.amount, "narration": t.narration, "category": t.category}
            for t in large_txns
        ]
    } 

def build_prompt(data: dict, month: int, year: int)->str:
    current = data['current']
    previous = data['previous']
    budgets = data['budgets']
    large_txns = data['large_txns']

    increases = []

    for cat, amt in current.items():
        prev = previous.get(cat,0)
        if prev>0:
            change = ((amt-prev)/prev)*100

            if change>20:
                increases.append(f"{cat}: ₹{prev:.0f} -> ₹{amt:.0f} (+{change:.1f}%)")

    overruns = []
    for cat, limit in budgets.items():
        spent = current.get(cat,0)
        if spent>limit:
            overruns.append(f"{cat}: limit ₹{limit:.0f}, spent ₹{spent:.0f}")

    prompt = f"""
                You are a personal finance assistant analyzing Indian bank transactions.

                Month: {month}/{year}

                Category spending this month:
                {chr(10).join(f"- {k}: ₹{v:.0f}" for k, v in current.items())}

                Spending increases vs last month:
                {chr(10).join(increases) if increases else "None"}

                Budget overruns:
                {chr(10).join(overruns) if overruns else "None"}

                Top 5 largest transactions:
                {chr(10).join(f"- ₹{t['amount']:.0f} | {t['narration']} | {t['category']}" for t in large_txns)}

                Give 4-5 short, specific, actionable insights in simple English.
                Each insight should be one sentence.
                Focus on unusual patterns, overspending, and saving opportunities.
                """
    return prompt

def get_ai_insights(prompt: str)->list[str]:
    
    
    client = Groq(api_key=os.getenv("GROQ_QPI_KEY"))

    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5
    )

    raw = response.choices[0].message.content

    insights = [
        line.strip("•-123456789. ").strip()
        for line in raw.strip().split("\n")
        if line.strip() and len(line.strip()) > 10
    ]

    return insights
