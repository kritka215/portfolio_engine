# portfolio_engine.py

ASSET_RULES = {
    "Conservative": {
        "Debt": 45,
        "SWP": 25,
        "Gold": 15,
        "REITs": 15
    },
    "Moderate": {
        "Equity": 50,
        "Debt": 30,
        "Gold": 10,
        "REITs": 10
    },
    "Aggressive": {
        "Equity": 65,
        "AIF": 15,
        "Commodities": 10,
        "Crypto": 10
    }
}

def build_skeleton_portfolio(bucket):
    return ASSET_RULES[bucket]


def explain_portfolio(portfolio, risk_score):
    explanation = []
    for asset, weight in portfolio.items():
        explanation.append(
            f"{asset}: {weight}% allocated based on risk score {risk_score}"
        )
    return "\n".join(explanation)
