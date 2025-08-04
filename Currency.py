import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import time
from datetime import datetime

# Constants
CACHE_TTL = 600  # seconds
PRIMARY_API = "https://api.exchangerate-api.com/v4/latest/{base}"
FALLBACK_API = "https://api.exchangerate.host/latest?base={base}&symbols={symbol_list}"

CURRENCY_LIST = [
    "USD", "PKR", "EUR", "INR", "CAD", "GBP", "AUD", "JPY", "CNY",
    "SGD", "CHF", "NZD", "AED", "SAR", "HKD", "THB", "MYR", "KRW"
]

SYMBOL_MAP = {
    "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CNY": "¥", "INR": "₹",
    "PKR": "₨", "AUD": "A$", "CAD": "C$", "CHF": "CHF", "SGD": "S$", "NZD": "NZ$",
    "AED": "د.إ", "SAR": "ر.س", "HKD": "HK$", "THB": "฿", "MYR": "RM", "KRW": "₩"
}

# Emoji/flag mapping (fallback to simple text if not available)
FLAG_EMOJI = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵", "CNY": "🇨🇳",
    "INR": "🇮🇳", "PKR": "🇵🇰", "AUD": "🇦🇺", "CAD": "🇨🇦", "SGD": "🇸🇬",
    "CHF": "🇨🇭", "NZD": "🇳🇿", "AED": "🇦🇪", "SAR": "🇸🇦", "HKD": "🇭🇰",
    "THB": "🇹🇭", "MYR": "🇲🇾", "KRW": "🇰🇷"
}

# Simple in-memory cache
_rate_cache = {}  # key: base currency, value: (timestamp, rates dict)

def format_amount(amount):
    try:
        if abs(amount) >= 1:
            return f"{amount:,.2f}"
        else:
            return f"{amount:.6f}"
    except Exception:
        return str(amount)

def fetch_rates(base):
    now = time.time()
    cached = _rate_cache.get(base)
    if cached and now - cached[0] < CACHE_TTL:
        return cached[1], cached[0]

    try:
        resp = requests.get(PRIMARY_API.format(base=base), timeout=5)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates")
        if rates:
            _rate_cache[base] = (now, rates)
            return rates, now
    except Exception:
        pass

    try:
        symbol_list = ",".join(CURRENCY_LIST)
        resp = requests.get(FALLBACK_API.format(base=base, symbol_list=symbol_list), timeout=5)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates")
        if rates:
            _rate_cache[base] = (now, rates)
            return rates, now
    except Exception as e:
        raise RuntimeError(f"Both rate sources failed: {e}")

    raise RuntimeError("Failed to retrieve exchange rates.")

class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Currency Converter")
        self.geometry("500x600")
        self.configure(bg="#f0f4f7")
        self.resizable(False, False)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 11, "bold"))
        self.style.map("TButton",
                       background=[("active", "#005fa3"), ("!disabled", "#007acc")],
                       foreground=[("!disabled", "white")])
        self.style.configure("TLabel", background="#f0f4f7", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("Result.TLabel", font=("Segoe UI", 14), foreground="#1f2d3a")
        self.style.configure("Sub.TLabel", font=("Segoe UI", 9), foreground="#555")

        self._build_ui()
        self.bind("<Return>", lambda e: self.convert_currency())

    def _build_ui(self):
        title = ttk.Label(self, text="Currency Converter", style="Header.TLabel")
        title.pack(pady=(15, 5))

        input_frame = ttk.Frame(self)
        input_frame.pack(padx=25, pady=10, fill="x")

        # Amount
        amt_label = ttk.Label(input_frame, text="Amount:")
        amt_label.grid(row=0, column=0, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, font=("Segoe UI", 12))
        self.amount_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        input_frame.columnconfigure(0, weight=1)

        # Currency selectors with emoji labels
        from_frame = ttk.Frame(input_frame)
        from_frame.grid(row=2, column=0, padx=(0, 5), sticky="ew")
        to_frame = ttk.Frame(input_frame)
        to_frame.grid(row=2, column=1, padx=(5, 5), sticky="ew")

        # From
        ttk.Label(from_frame, text="From:").pack(anchor="w")
        sel_frame_a = ttk.Frame(from_frame)
        sel_frame_a.pack(fill="x")
        self.from_flag = ttk.Label(sel_frame_a, text=FLAG_EMOJI.get("USD", "USD"), font=("Segoe UI", 24))
        self.from_flag.pack(side="left", padx=(0, 5))
        self.from_currency = ttk.Combobox(sel_frame_a, values=CURRENCY_LIST, font=("Segoe UI", 11), state="readonly", width=8)
        self.from_currency.set("USD")
        self.from_currency.pack(side="left", fill="x", expand=True)
        self.from_currency.bind("<<ComboboxSelected>>", lambda e: self._refresh_flags())

        # To
        ttk.Label(to_frame, text="To:").pack(anchor="w")
        sel_frame_b = ttk.Frame(to_frame)
        sel_frame_b.pack(fill="x")
        self.to_flag = ttk.Label(sel_frame_b, text=FLAG_EMOJI.get("PKR", "PKR"), font=("Segoe UI", 24))
        self.to_flag.pack(side="left", padx=(0, 5))
        self.to_currency = ttk.Combobox(sel_frame_b, values=CURRENCY_LIST, font=("Segoe UI", 11), state="readonly", width=8)
        self.to_currency.set("PKR")
        self.to_currency.pack(side="left", fill="x", expand=True)
        self.to_currency.bind("<<ComboboxSelected>>", lambda e: self._refresh_flags())

        # Swap button
        swap_btn = ttk.Button(input_frame, text="⇄ Swap", command=self._swap_currencies)
        swap_btn.grid(row=2, column=2, padx=(10, 0), sticky="ns", pady=(18, 0))

        # Convert button
        self.convert_btn = ttk.Button(self, text="Convert", command=self.convert_currency)
        self.convert_btn.pack(pady=10, ipadx=10)

        # Result display
        self.result_label = ttk.Label(self, text="", style="Result.TLabel", anchor="center", wraplength=450, justify="center")
        self.result_label.pack(pady=(5, 2))

        self.last_updated_label = ttk.Label(self, text="", style="Sub.TLabel")
        self.last_updated_label.pack()

        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5)
        self.copy_btn = ttk.Button(action_frame, text="Copy Result", command=self._copy_result, state="disabled")
        self.copy_btn.grid(row=0, column=0, padx=5)
        self.refresh_btn = ttk.Button(action_frame, text="Refresh Rates", command=self._manual_refresh)
        self.refresh_btn.grid(row=0, column=1, padx=5)

        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", pady=10, padx=20)

        history_label = ttk.Label(self, text="Conversion History")
        history_label.pack(anchor="w", padx=25)
        self.history_listbox = tk.Listbox(self, height=6, bd=0, highlightthickness=0, font=("Segoe UI", 10))
        self.history_listbox.pack(fill="both", padx=25, pady=(5, 5))
        self.history = []

        clear_hist_btn = ttk.Button(self, text="Clear History", command=self._clear_history)
        clear_hist_btn.pack(pady=(0, 10))

        footer = ttk.Label(self, text="Rates cached for 10 minutes. Emoji represents currencies.", style="Sub.TLabel")
        footer.pack(side="bottom", pady=5)

        # initial flags
        self._refresh_flags()

    def _refresh_flags(self):
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        self.from_flag.config(text=FLAG_EMOJI.get(from_curr, from_curr))
        self.to_flag.config(text=FLAG_EMOJI.get(to_curr, to_curr))

    def _swap_currencies(self):
        a = self.from_currency.get()
        b = self.to_currency.get()
        self.from_currency.set(b)
        self.to_currency.set(a)
        self._refresh_flags()
        self.convert_currency()

    def _set_loading(self, loading=True):
        if loading:
            self.convert_btn.config(text="Converting...", state="disabled")
        else:
            self.convert_btn.config(text="Convert", state="normal")

    def convert_currency(self):
        try:
            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                raise ValueError("Amount is empty.")
            amount = float(amount_str.replace(",", ""))
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid numeric amount.")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        if not from_curr or not to_curr:
            messagebox.showerror("Input Error", "Select both currencies.")
            return

        threading.Thread(target=self._do_conversion, args=(amount, from_curr, to_curr), daemon=True).start()
        self._set_loading(True)
        self.result_label.config(text="Fetching rate...")

    def _do_conversion(self, amount, from_curr, to_curr):
        try:
            rates, timestamp = fetch_rates(from_curr)
            rate = rates.get(to_curr)
            if rate is None:
                raise RuntimeError(f"No rate available for {to_curr} from {from_curr}.")
            converted = amount * rate
            symbol_from = SYMBOL_MAP.get(from_curr, from_curr)
            symbol_to = SYMBOL_MAP.get(to_curr, to_curr)
            formatted_src = format_amount(amount)
            formatted_dest = format_amount(converted)
            flag_from = FLAG_EMOJI.get(from_curr, from_curr)
            flag_to = FLAG_EMOJI.get(to_curr, to_curr)
            result_text = f"{flag_from} {symbol_from}{formatted_src} {from_curr} = {flag_to} {symbol_to}{formatted_dest} {to_curr}"
            updated_time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            self.after(0, self._update_result, result_text, updated_time_str, amount, from_curr, to_curr, formatted_src, formatted_dest)
        except Exception as e:
            self.after(0, self._handle_conversion_error, str(e))

    def _update_result(self, result_text, updated_time, amount, from_curr, to_curr, fsrc, fdest):
        self.result_label.config(text=result_text)
        self.last_updated_label.config(text=f"Rate last updated: {updated_time}")
        self._set_loading(False)
        self.copy_btn.config(state="normal")
        hist_entry = f"{fsrc} {from_curr} → {fdest} {to_curr} ({datetime.now().strftime('%H:%M:%S')})"
        self.history.insert(0, hist_entry)
        if len(self.history) > 20:
            self.history = self.history[:20]
        self._refresh_history_listbox()

    def _handle_conversion_error(self, error_msg):
        self.result_label.config(text="Conversion failed.")
        self.last_updated_label.config(text="")
        self._set_loading(False)
        messagebox.showerror("Conversion Error", f"Could not convert currency:\n{error_msg}")

    def _refresh_history_listbox(self):
        self.history_listbox.delete(0, tk.END)
        for item in self.history:
            self.history_listbox.insert(tk.END, item)

    def _clear_history(self):
        self.history = []
        self._refresh_history_listbox()

    def _copy_result(self):
        result = self.result_label.cget("text")
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("Copied", "Result copied to clipboard.")

    def _manual_refresh(self):
        base = self.from_currency.get()
        if base in _rate_cache:
            del _rate_cache[base]
        self.convert_currency()

if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()
