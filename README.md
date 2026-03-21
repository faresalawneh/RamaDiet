# 🌙 RamaDiet 🇯🇴
### AI-Powered Nutrition Planner for a Healthier & Inclusive Ramadan

Built during the **#Hack_Ramadan Hackathon** (March 2026) by team **"The Overfitters"**.

RamaDiet is an AI meal planner that generates customized Suhoor and Iftar plans using authentic Jordanian cuisine, powered by a RAG pipeline and Google Gemini 2.5 Flash.

---

## ✨ Key Features

- **🤖 AI Customization:** Gemini 2.5 Flash analyzes your stats (weight, goal, activity level) and generates a macro-balanced plan for weight loss, muscle gain, or maintenance.
- **🥘 Authentic Jordanian Menu:** Local favorites like Mansaf, Maqluba, and Mujadara — intelligently portioned for your goals.
- **🏥 Medical Context Aware:** Dynamically filters high-sodium or high-sugar ingredients for users with Hypertension or Diabetes.
- **🎛️ Interactive Macros:** Adjust ingredient weights on the fly and watch calories, protein, and carbs update in real time.
- **💬 "Shagardi" AI Chatbot:** A bilingual (Arabic/English) diet and workout coach tuned to the Jordanian dialect.
- **🔄 Smart Swaps:** Healthy localized alternatives for high-calorie cravings (e.g. Qatayef).
- **💧 Hydration & Grocery Logic:** Calculates water intake needs and generates a downloadable shopping list.

---

## 🗂️ Project Structure

```
RamaDiet/
├── app.py                  # Main Streamlit application
├── normalize_to_100g.py    # Dataset normalization script
├── ramadan_100g.csv        # Jordanian food nutrition dataset (153 items)
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/faresalawneh/RamaDiet.git
cd RamaDiet
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Gemini API key
```bash
export GOOGLE_API_KEY="your_api_key_here"
```
Get a free key at [aistudio.google.com](https://aistudio.google.com)

### 4. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🧠 How It Works

1. User inputs personal stats (weight, height, goal, medical conditions)
2. A RAG pipeline performs cosine similarity search over the 153-item Jordanian nutrition dataset
3. Gemini 2.5 Flash selects food names and portions — nutritional values are fetched directly from CSV to prevent hallucination
4. The app builds a complete Suhoor + Iftar plan with real-time macro tracking

---

## 📦 Dataset

A custom 153-item Jordanian food nutrition dataset, normalized to 100g servings.

| Column | Description |
|--------|-------------|
| `Food` | Food item name (Arabic/English) |
| `Calories` | Per 100g |
| `Protein` | Per 100g (g) |
| `Carbs` | Per 100g (g) |
| `Fat` | Per 100g (g) |
| `Sodium` | Per 100g (mg) |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI/LLM:** Google Gemini 2.5 Flash
- **RAG:** Cosine similarity over nutrition dataset
- **Data:** Pandas
- **Language:** Python

---

## 👥 Team — The Overfitters

Built at **#Hack_Ramadan Hackathon**, March 2026.

---

## 📝 License

MIT License
