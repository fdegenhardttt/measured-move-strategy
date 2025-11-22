import pandas as pd
import plotly.io as pio
from visualization import plot_interactive_chart
import os
from datetime import datetime

def generate_html_report(results: list, filename: str = None):
    """
    Generates a self-contained HTML report with summary table and interactive charts.
    """
    if not filename:
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"daily_report_{date_str}.html"
        
    html_content = f"""
    <html>
    <head>
        <title>Measured Move Daily Report</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f5f5f7; color: #1d1d1f; padding: 20px; }}
            h1 {{ text-align: center; color: #1d1d1f; }}
            .summary-table {{ width: 100%; border-collapse: collapse; margin-bottom: 40px; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.05); }}
            .summary-table th, .summary-table td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
            .summary-table th {{ background-color: #0071e3; color: white; }}
            .chart-container {{ background: white; border-radius: 18px; padding: 20px; margin-bottom: 30px; box-shadow: 0 4px 24px rgba(0,0,0,0.05); }}
            .bullish {{ color: green; font-weight: bold; }}
            .bearish {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Daily Measured Move Report - {datetime.now().strftime("%Y-%m-%d")}</h1>
        
        <h2>Summary of Opportunities</h2>
    """
    
    if not results:
        html_content += "<p>No opportunities found matching criteria today.</p></body></html>"
        with open(filename, "w") as f:
            f.write(html_content)
        return filename

    # Create Summary Table
    html_content += "<table class='summary-table'><thead><tr><th>Symbol</th><th>Direction</th><th>Price</th><th>Target (D)</th><th>Dist to Target %</th></tr></thead><tbody>"
    
    for res in results:
        direction_class = "bullish" if res['Direction'] == "Bullish" else "bearish"
        html_content += f"""
        <tr>
            <td>{res['Symbol']}</td>
            <td class='{direction_class}'>{res['Direction']}</td>
            <td>{res['Price']:.2f}</td>
            <td>{res['Target (D)']:.2f}</td>
            <td>{res['Dist to Target %']:.2f}%</td>
        </tr>
        """
    html_content += "</tbody></table>"
    
    # Create Charts
    html_content += "<h2>Detailed Charts</h2>"
    
    for res in results:
        fig = plot_interactive_chart(res['DataFrame'], res['Pivots'], res['Moves'], res['Symbol'])
        # Convert Plotly fig to HTML div
        plot_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
        
        html_content += f"""
        <div class="chart-container">
            <h3>{res['Symbol']} - {res['Direction']} (Target: {res['Target (D)']:.2f})</h3>
            {plot_html}
        </div>
        """
        
    html_content += "</body></html>"
    
    with open(filename, "w") as f:
        f.write(html_content)
        
    return filename
