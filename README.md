# Spa AI Automation System

A comprehensive AI-powered automation system for spa businesses that handles bookings, customer inquiries, and appointment management without human intervention.

## Features

- 🤖 **AI-Powered Customer Service** - RAG-based chatbot for inquiries
- 📅 **Automated Booking System** - Complete booking workflow
- 📧 **Email Automation** - Confirmation emails to clients and spa managers
- 📊 **Google Calendar Integration** - Automatic appointment scheduling
- 📈 **Google Sheets Tracking** - Booking analytics and management
- 🎨 **Modern Animated Frontend** - Beautiful React-based UI
- 🔒 **Secure & Scalable** - Built with FastAPI and modern practices

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - RAG implementation
- **ChromaDB** - Vector database
- **SQLAlchemy** - Database ORM
- **Google APIs** - Calendar and Sheets integration

### Frontend
- **React** - Modern UI framework
- **Framer Motion** - Smooth animations
- **Tailwind CSS** - Styling
- **Axios** - API communication

### Free APIs Used
- **Resend** - Email service (free tier)
- **Google Calendar API** - Appointment scheduling
- **Google Sheets API** - Data tracking
- **OpenAI API** - AI capabilities (free tier available)

## Quick Start

1. **Clone and Setup**
```bash
git clone <repository>
cd spa-ai-automation
pip install -r requirements.txt
```

2. **Environment Setup**
```bash
cp .env.example .env
# Fill in your API keys and configuration
```

3. **Run Backend**
```bash
python main.py
```

4. **Run Frontend**
```bash
cd frontend
npm install
npm start
```

## Configuration

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
RESEND_API_KEY=your_resend_key
SPA_MANAGER_EMAIL=manager@yourspa.com
```

## System Architecture

```
Frontend (React) → Backend (FastAPI) → AI Services → Google APIs
     ↓                    ↓                ↓           ↓
  User Interface    Business Logic    RAG System   Calendar/Sheets
```

## API Endpoints

- `POST /api/book` - Create new booking
- `POST /api/inquiry` - Handle customer inquiry
- `GET /api/services` - Get available services
- `POST /api/chat` - AI chatbot endpoint

## License

MIT License - Free to use and modify
