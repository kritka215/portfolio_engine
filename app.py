import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from risk_engine import calculate_risk_score, risk_bucket
from portfolio_engine import build_skeleton_portfolio
import random

# --- Helper Functions for Analytics (Simulated) ---
def calculate_metrics(risk_score, portfolio):
    # Simulate metrics based on risk score
    # Higher risk -> Higher expected return, higher volatility
    base_return = 6.0
    risk_premium = (risk_score / 100) * 8.0  # Max 14%
    expected_return = base_return + risk_premium
    
    volatility = (risk_score / 100) * 15.0 + 3.0 # Min 3%, Max 18%
    sharpe = expected_return / volatility if volatility > 0 else 0
    
    return {
        "Risk Score": risk_score,
        "Exp. Return": f"{expected_return:.1f}%",
        "Volatility": f"{volatility:.1f}%",
        "Sharpe Ratio": f"{sharpe:.2f}"
    }

def generate_charts(portfolio, profile, horizon):
    # 1. Asset Allocation Donut
    df_alloc = pd.DataFrame(list(portfolio.items()), columns=["Asset", "Weight"])
    fig_alloc = px.pie(df_alloc, values="Weight", names="Asset", hole=0.5, 
                       color_discrete_sequence=px.colors.qualitative.Bold,
                       title="Portfolio Distribution")
    fig_alloc.update_layout(showlegend=True, margin=dict(l=20, r=20, t=40, b=20))

    # 2. Projected Growth (Simulated Area Chart)
    years = 10
    if "3-7" in horizon: years = 5
    elif "<3" in horizon: years = 3
    
    x_axis = [f"Year {i}" for i in range(years + 1)]
    base_val = 10000 
    growth_rate = 0.08  # Default
    if profile == "Conservative": growth_rate = 0.05
    elif profile == "Aggressive": growth_rate = 0.12
    
    y_vals = [base_val * ((1 + growth_rate) ** i) for i in range(years + 1)]
    y_vals_conservative = [base_val * ((1 + growth_rate - 0.02) ** i) for i in range(years + 1)]
    y_vals_optimistic = [base_val * ((1 + growth_rate + 0.02) ** i) for i in range(years + 1)]
    
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Scatter(x=x_axis, y=y_vals, fill='tozeroy', name='Base Case', line=dict(color='#636EFA')))
    fig_growth.add_trace(go.Scatter(x=x_axis, y=y_vals_optimistic, name='Optimistic', line=dict(color='#00CC96', dash='dot')))
    fig_growth.update_layout(title="Wealth Projection (Monte Carlo Sim)", xaxis_title="Timeline", yaxis_title="Value ($)", hovermode="x unified")

    return fig_alloc, fig_growth, df_alloc

# --- Main Logic ---
def update_dashboard(profile, goal, horizon, liquidity, volatility):
    # 1. Core Engines
    score = calculate_risk_score(profile, horizon, goal, liquidity, volatility)
    bucket = risk_bucket(score)
    portfolio = build_skeleton_portfolio(bucket)
    
    # 2. Metrics
    metrics = calculate_metrics(score, portfolio)
    
    # 3. Charts
    fig_alloc, fig_growth, df_alloc = generate_charts(portfolio, profile, horizon)
    
    return (
        metrics["Risk Score"], 
        metrics["Exp. Return"], 
        metrics["Volatility"], 
        metrics["Sharpe Ratio"],
        bucket,
        fig_alloc, 
        fig_growth,
        df_alloc
    )

# --- UI Layout ---
custom_css = """
body { background-color: #f0f2f6; }
.gradio-container { font-family: 'Roboto', sans-serif; }
.metric-card {
    background: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
}
.metric-label {
    font-size: 12px;
    color: #7f8c8d;
    text-transform: uppercase;
    letter-spacing: 1px;
}
"""

theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate",
).set(
    body_background_fill="#f9fafb",
    block_background_fill="#ffffff",
    block_border_width="0px",
    block_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
)

with gr.Blocks(theme=theme, css=custom_css, title="Portfolio Dashboard") as demo:
    
    # Header
    with gr.Row():
        with gr.Column(scale=1):
             gr.Image("https://cdn-icons-png.flaticon.com/512/4202/4202619.png", height=40, show_label=False, container=False)
        with gr.Column(scale=10):
            gr.Markdown("# 🚀 Project Portfolio Dashboard\n### AI-Powered Investment Intelligence")
            
    # Main Content
    with gr.Row():
        # --- Sidebar ---
        with gr.Column(scale=1, min_width=300):
            gr.Markdown("### ⚙️ Configuration")
            with gr.Group():
                profile_in = gr.Dropdown(["Conservative", "Moderate", "Aggressive"], value="Moderate", label="Risk Profile")
                goal_in = gr.Dropdown(["Capital Preservation", "Income", "Balanced Growth", "Wealth Creation"], value="Balanced Growth", label="Investment Goal")
                horizon_in = gr.Dropdown(["<3 yrs", "3-7 yrs", "7+ yrs"], value="7+ yrs", label="Time Horizon")
                liquidity_in = gr.Dropdown(["High", "Medium", "Low"], value="Medium", label="Liquidity")
                volatility_in = gr.Slider(0, 10, value=6, label="Volatility Tolerance")
                
                generate_btn = gr.Button("🔄 Generate Portfolio", variant="primary", size="lg")
        
        # --- Dashboard Area ---
        with gr.Column(scale=3):
            # Key Metrics Row
            with gr.Row():
                with gr.Column(variant="panel"):
                    m_score = gr.Number(label="Risk Score", value=0, precision=0)
                with gr.Column(variant="panel"):
                    m_return = gr.Textbox(label="Expected Return", value="--")
                with gr.Column(variant="panel"):
                    m_vol = gr.Textbox(label="Volatility", value="--")
                with gr.Column(variant="panel"):
                    m_sharpe = gr.Textbox(label="Sharpe Ratio", value="--")
                with gr.Column(variant="panel"):
                    m_bucket = gr.Textbox(label="Risk Category", value="--")

            # Chart Row 1
            with gr.Row():
                chart_alloc = gr.Plot(label="Asset Allocation")
                chart_growth = gr.Plot(label="Projected Wealth")
            
            # Detailed Breakdown
            gr.Markdown("### 📋 Asset Breakdown Table")
            table_details = gr.Dataframe(
                headers=["Asset", "Weight"],
                label="Portfolio Composition"
            )

    # Interactions
    inputs = [profile_in, goal_in, horizon_in, liquidity_in, volatility_in]
    outputs = [m_score, m_return, m_vol, m_sharpe, m_bucket, chart_alloc, chart_growth, table_details]
    
    generate_btn.click(fn=update_dashboard, inputs=inputs, outputs=outputs)
    
    # Load default on startup
    demo.load(fn=update_dashboard, inputs=inputs, outputs=outputs)

if __name__ == "__main__":
    demo.launch()
