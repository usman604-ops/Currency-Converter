# Currency-Converter
Currency Converter
💱 Currency Converter Desktop App (Tkinter + Real-time APIs)
A modern, user-friendly Currency Converter desktop application built using Python's Tkinter GUI toolkit. The app fetches real-time exchange rates from reliable APIs and provides fast, accurate currency conversions between 18 major global currencies. 🧮🌍
🚀 Features
🔄 Live Conversion: Fetches real-time rates using ExchangeRate-API and a fallback to ExchangeRate.host.

🧠 Smart Caching: Caches exchange rates for 10 minutes to reduce API calls and improve performance.

✨ Modern UI: Clean, intuitive interface styled with ttk themes and emojis/flags for a better user experience.

🔁 Swap Functionality: Instantly swap currencies with one click.

📜 Conversion History: Keeps track of your recent conversions (up to 20).

📋 Copy Result: Copy the latest conversion result to clipboard.

🔄 Manual Refresh: Force refresh the rates cache at any time.

🌐 18 Supported Currencies: Including USD, PKR, EUR, INR, GBP, JPY, AUD, CNY, and more.

🧑‍💻 Tech Stack
Language: Python 3.x

GUI Framework: Tkinter + ttk

API Services:

ExchangeRate-API (Primary)

ExchangeRate.host (Fallback)

Multithreading: For non-blocking API requests and smooth UI experience.

