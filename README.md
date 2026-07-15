# 🧠 AI-First CRM HCP Module

A modern, AI-powered **Customer Relationship Management (CRM)** module built for **Life Sciences field representatives** to efficiently log and manage interactions with **Healthcare Professionals (HCPs)**.

The application supports both:

- 📝 **Traditional structured form-based interaction logging**
- 💬 **Conversational AI-powered interaction logging**

The AI assistant understands natural language, extracts structured information (such as HCP names, meeting topics, sentiment, materials discussed, and samples shared), and synchronizes the extracted data with the application's UI in real time.

---

# ✨ Features

- 🤖 AI-powered conversational interaction logging
- 📝 Traditional CRM interaction form
- 🔄 Real-time AI entity extraction and UI binding
- 😊 Automatic sentiment analysis
- 📋 AI-generated follow-up recommendations
- 📚 HCP interaction history retrieval
- ✏️ Edit existing interactions conversationally
- ⚡ Fast, modern React frontend
- 🚀 High-performance FastAPI backend
- 🧠 LangGraph agent workflow
- ✅ Strict request validation using Pydantic

---

# 🏗️ Architecture

```
User
   │
   ▼
React + Redux Frontend
   │
Axios API Calls
   │
   ▼
FastAPI Backend
   │
LangGraph Agent
   │
Groq LLM (llama-3.3-70b-versatile)
   │
AI Tools
   ├── Log Interaction
   ├── Edit Interaction
   ├── Analyze Sentiment
   ├── Suggest Follow-ups
   └── Fetch HCP History
```

---

# 🚀 Tech Stack

## Frontend

- React (JSX)
- Redux Toolkit
- Axios
- CSS
- Google Inter Font

## Backend

- Python
- FastAPI
- LangGraph
- Groq API
- Pydantic
- SQLAlchemy + MySQL (via PyMySQL)

---

# 🧠 AI Agent (LangGraph)

The AI assistant is implemented using **LangGraph**, enabling an agentic workflow with specialized tools for CRM operations.

## Implemented AI Tools

### 1. 📝 Log Interaction (Mandatory)

Extracts structured CRM information from natural language conversations.

Extracted entities include:

- HCP Name
- Meeting Topics
- Samples Shared
- Marketing Materials
- Notes
- Discussion Summary

The extracted information is automatically logged into the CRM database.

---

### 2. ✏️ Edit Interaction (Mandatory)

Allows users to conversationally modify previously recorded interactions.

Example:

> "Actually the doctor requested 10 samples instead of 5."

The AI identifies the record and updates the corresponding fields.

---

### 3. 😊 Analyze Sentiment (Sales)

Automatically analyzes the overall tone of the interaction.

Supported labels:

- Positive
- Neutral
- Negative

This helps sales representatives prioritize future engagements.

---

### 4. 📋 Suggest Follow-ups (Sales)

Generates intelligent next-step recommendations based on:

- Discussion topics
- Doctor interests
- Meeting outcomes
- Sentiment analysis

Examples include:

- Schedule another visit
- Share additional product literature
- Arrange a product demonstration
- Send requested clinical evidence

---

### 5. 📚 Fetch HCP History (Sales)

Retrieves previous interaction history for a selected healthcare professional, allowing representatives to maintain context before future meetings.

---

# 🤖 AI Model

The application uses the following Groq-hosted Large Language Model:

**Model**

```
llama-3.3-70b-versatile
```

> **Note**
>
> The originally requested **gemma2-9b-it** model has been decommissioned by Groq. The application therefore uses **llama-3.3-70b-versatile** as the designated fallback model for conversational context parsing and structured data extraction.

---

# 📁 Project Structure

```
AI-First-CRM/
│
├── ai-backend/
│   ├── main.py
│   ├── agent.py
│   ├── schema.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env
│   └── ...
│
├── hcp-crm-ui/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
└── README.md
```

---

# 🛠️ Local Installation & Setup

The project consists of two applications:

- Backend (FastAPI + LangGraph)
- Frontend (React)

Run both simultaneously using separate terminal windows.

## Before you start

The backend needs a running **MySQL** server it can reach. `database.py` connects and creates the `interactions` table the moment the app starts up, so if MySQL isn't running yet (or the connection details are wrong), the backend will fail immediately on launch rather than later when you first use it. Have MySQL up and a database created before running `python main.py`.

---

# 1️⃣ Backend Setup

Navigate to the backend directory.

```bash
cd ai-backend
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file inside the backend directory with **both** of the following — the app raises an error on startup if either is missing.

```env
GROQ_API_KEY=your_api_key_here
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/your_db_name
```

`DATABASE_URL` follows SQLAlchemy's connection string format. Make sure the database (`your_db_name` above) already exists on your MySQL server — SQLAlchemy will create the `interactions` table for you, but not the database itself.

---

## Start the Backend

```bash
python main.py
```

Backend URL

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# 2️⃣ Frontend Setup

Open another terminal.

Navigate to the frontend.

```bash
cd hcp-crm-ui
```

Install dependencies.

```bash
npm install
```

Run the application.

```bash
npm run dev
```

or

```bash
npm start
```

Frontend URL

```
http://localhost:3000
```

---

# 💬 Example AI Conversation

### User

> Met Dr. Sharma today. Discussed diabetes management. Shared 5 Jardiance samples and product brochure. Doctor seemed interested and requested another meeting next month.

### AI Extracts

- HCP Name → Dr. Sharma
- Topic → Diabetes Management
- Samples → Jardiance (5)
- Materials → Product Brochure
- Sentiment → Positive
- Follow-up → Schedule meeting next month

---

# 📌 API Documentation

Once the backend is running, FastAPI automatically generates interactive API documentation.

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# 🎯 Future Enhancements

- Voice-based interaction logging
- OCR support for handwritten notes
- Calendar integration
- Email follow-up automation
- Multi-language support
- Offline-first synchronization
- Dashboard analytics
- Role-based authentication
- Cloud database integration

---

# 👨‍💻 Author

**Dhananjay Madan Salwe**

**Full Stack Developer**

---

# 📄 License

This project is intended for demonstration and educational purposes.