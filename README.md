# 🥗 MacroSnap

MacroSnap is an AI-powered nutrition assistant that analyzes meal photos or text descriptions and provides estimated calories and macronutrients.

The application uses Google's Gemini AI to analyze food and generate nutrition information. Users can then send their daily nutrition summary directly to Telegram.

## 🚀 Features

- 📷 Analyze meal images
- 💬 Describe meals using text
- 🤖 AI-powered food analysis using Gemini
- 🔥 Estimate calories
- 💪 Estimate protein
- 🍚 Estimate carbohydrates
- 🥑 Estimate fats
- 📊 Generate a daily nutrition summary
- 📱 Send the nutrition summary to Telegram
- 💻 Simple Streamlit web interface

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Telegram Bot API
- Requests

## 📁 Project Structure

```text
MacroSnap/
│
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml.example