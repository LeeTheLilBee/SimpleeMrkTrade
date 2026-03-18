import io
import contextlib
import yfinance as yf

def safe_download(symbol, period="3mo", auto_adjust=True, progress=False):
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            df = yf.download(symbol, period=period, auto_adjust=auto_adjust, progress=progress)
        return df
    except Exception:
        return None
