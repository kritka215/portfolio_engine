# risk_engine.py

RISK_PROFILE_SCORE = {
    "Conservative": 10,
    "Moderate": 20,
    "Aggressive": 30
}

TIME_HORIZON_SCORE = {
    "<3 yrs": 5,
    "3-7 yrs": 15,
    "7+ yrs": 25
}

GOAL_SCORE = {
    "Capital Preservation": 5,
    "Income": 10,
    "Balanced Growth": 15,
    "Wealth Creation": 20
}

LIQUIDITY_SCORE = {
    "High": 5,
    "Medium": 10,
    "Low": 15
}

def calculate_risk_score(profile, horizon, goal, liquidity, volatility):
    score = (
        RISK_PROFILE_SCORE[profile]
        + TIME_HORIZON_SCORE[horizon]
        + GOAL_SCORE[goal]
        + LIQUIDITY_SCORE[liquidity]
        + volatility
    )
    return min(score, 100)


def risk_bucket(score):
    if score <= 30:
        return "Conservative"
    elif score <= 60:
        return "Moderate"
    else:
        return "Aggressive"
