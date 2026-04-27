"""
Fractal Dimension of Stock Prices - Flask App

Run with:
    pip install flask yfinance numpy
    python app.py

Then visit http://localhost:5000
"""
from flask import Flask, render_template, request, jsonify
import yfinance as yf
import numpy as np
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stock', methods=['GET'])
def get_stock():
    """Fetch stock price data for a given ticker and date range."""
    ticker = request.args.get('ticker', 'AAPL').upper().strip()
    start = request.args.get('start', '2020-01-01')
    end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))

    try:
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if df.empty:
            return jsonify({'error': f'No data found for ticker "{ticker}" in given range'}), 404

        # Handle multi-level columns from yfinance
        if hasattr(df.columns, 'levels'):
            close_col = df['Close'][ticker] if ticker in df['Close'].columns else df['Close'].iloc[:, 0]
        else:
            close_col = df['Close']

        prices = close_col.values.astype(float).tolist()
        dates = [d.strftime('%Y-%m-%d') for d in df.index]

        # Compute log returns server-side (more accurate than JS)
        log_returns = np.diff(np.log(prices)).tolist()

        return jsonify({
            'ticker': ticker,
            'dates': dates,
            'prices': prices,
            'log_returns': log_returns,
            'count': len(prices)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)