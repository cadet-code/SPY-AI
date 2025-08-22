# Spa AI Automation System - Setup Guide

This guide will help you set up the complete AI-powered spa automation system with booking, customer inquiries, and appointment management.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Git

### 1. Clone and Setup Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp env_example.txt .env

# Edit .env file with your API keys
nano .env

# Start the backend server
python main.py
```

### 2. Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## 🔧 Configuration

### Required API Keys

You'll need to obtain the following free API keys:

#### 1. OpenAI API Key
- Visit [OpenAI Platform](https://platform.openai.com/)
- Create an account and get your API key
- Free tier includes $18 credit

#### 2. Resend Email API
- Visit [Resend](https://resend.com/)
- Sign up for free account
- Get your API key (free tier: 3,000 emails/month)

#### 3. Google APIs (Optional)
- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project
- Enable Google Calendar API and Google Sheets API
- Create OAuth2 credentials

### Environment Variables

Update your `.env` file with the following:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
RESEND_API_KEY=your_resend_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Spa Configuration
SPA_MANAGER_EMAIL=manager@yourspa.com
SPA_NAME=Your Spa Name
SPA_ADDRESS=Your Spa Address
SPA_PHONE=Your Spa Phone

# Google Services (Optional)
GOOGLE_CALENDAR_ID=primary
GOOGLE_SHEETS_ID=your_google_sheets_id_here

# Database
DATABASE_URL=sqlite:///./spa_automation.db

# AI Configuration
AI_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000

# Appointment Settings
APPOINTMENT_DURATION=60
BUFFER_TIME=15
```

## 📁 Project Structure

```
spa-ai-automation/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── core/                   # Core configuration and database
│   ├── config.py          # Settings and configuration
│   └── database.py        # Database models and setup
├── api/                    # API routes
│   └── routes/
│       ├── booking.py     # Booking endpoints
│       ├── services.py    # Services endpoints
│       ├── inquiry.py     # Customer inquiry endpoints
│       └── chat.py        # AI chat endpoints
├── services/              # Business logic services
│   ├── ai_service.py      # AI/RAG functionality
│   ├── email_service.py   # Email automation
│   ├── google_calendar.py # Google Calendar integration
│   └── google_sheets.py   # Google Sheets integration
└── frontend/              # React frontend
    ├── package.json       # Node.js dependencies
    ├── src/
    │   ├── App.js         # Main React component
    │   ├── components/    # Reusable components
    │   └── pages/         # Page components
    └── public/            # Static assets
```

## 🎯 Features

### ✅ Implemented Features

1. **AI-Powered Booking System**
   - Multi-step booking form
   - Real-time availability checking
   - Service selection with pricing
   - Date and time picker

2. **Customer Inquiry Management**
   - Contact form with AI responses
   - Email notifications
   - Inquiry tracking

3. **AI Chatbot**
   - RAG-based responses
   - Real-time chat interface
   - Service information
   - Booking assistance

4. **Email Automation**
   - Booking confirmations
   - Manager notifications
   - Inquiry responses
   - Beautiful HTML templates

5. **Google Integration**
   - Calendar appointment scheduling
   - Sheets booking tracking
   - Analytics and reporting

6. **Modern Frontend**
   - Responsive design
   - Smooth animations
   - Beautiful UI/UX
   - Mobile-friendly

### 🔄 Automation Workflow

1. **Customer Books Appointment**
   - Fills out booking form
   - Selects service and time
   - Provides contact information
   - Receives confirmation email

2. **System Automatically**
   - Validates availability
   - Creates database record
   - Sends confirmation emails
   - Adds to Google Calendar
   - Updates Google Sheets
   - Notifies spa manager

3. **Customer Inquiries**
   - Customer submits inquiry
   - AI generates response
   - Email sent to customer
   - Manager notified
   - Inquiry tracked in database

## 🛠️ Development

### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# http://localhost:8000/docs
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Database Management

```bash
# The database is automatically created on first run
# SQLite database file: spa_automation.db

# To reset database
rm spa_automation.db
python main.py
```

## 🚀 Deployment

### Backend Deployment

1. **Using Python Anywhere (Free)**
   ```bash
   # Upload files to Python Anywhere
   # Set up virtual environment
   pip install -r requirements.txt
   
   # Configure WSGI file
   # Set environment variables
   ```

2. **Using Heroku**
   ```bash
   # Create Procfile
   echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
   
   # Deploy
   heroku create your-spa-app
   git push heroku main
   ```

3. **Using DigitalOcean/AWS**
   ```bash
   # Set up server
   # Install Python, Node.js
   # Configure nginx
   # Set up SSL certificates
   ```

### Frontend Deployment

1. **Using Netlify (Free)**
   ```bash
   cd frontend
   npm run build
   # Upload build folder to Netlify
   ```

2. **Using Vercel (Free)**
   ```bash
   # Connect GitHub repository
   # Vercel will auto-deploy
   ```

## 🔒 Security Considerations

1. **API Keys**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly

2. **Data Protection**
   - Implement rate limiting
   - Validate all inputs
   - Use HTTPS in production

3. **Privacy**
   - GDPR compliance for EU customers
   - Data retention policies
   - Customer consent management

## 📊 Monitoring and Analytics

### Built-in Analytics
- Booking success rates
- Service popularity
- Customer inquiries
- AI response quality

### Google Analytics Integration
```javascript
// Add to frontend/public/index.html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if database file exists
   ls -la spa_automation.db
   
   # Recreate database
   rm spa_automation.db
   python main.py
   ```

2. **Email Not Sending**
   - Check Resend API key
   - Verify email configuration
   - Check spam folder

3. **Google Integration Not Working**
   - Verify API credentials
   - Check API quotas
   - Ensure proper scopes

4. **Frontend Not Loading**
   ```bash
   # Clear cache
   npm cache clean --force
   
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   ```

### Support

For issues and questions:
1. Check the logs in the console
2. Review API documentation
3. Test individual components
4. Check network connectivity

## 🎉 Success Metrics

Track these metrics to measure success:

- **Booking Conversion Rate**: 70%+
- **Customer Satisfaction**: 4.5/5 stars
- **Response Time**: <2 seconds
- **Uptime**: 99.9%
- **Cost Savings**: 80% reduction in manual work

## 🔮 Future Enhancements

1. **Payment Integration**
   - Stripe/PayPal integration
   - Gift certificate purchases
   - Subscription packages

2. **Advanced AI Features**
   - Voice recognition
   - Multi-language support
   - Personalized recommendations

3. **Mobile App**
   - React Native app
   - Push notifications
   - Offline booking

4. **Analytics Dashboard**
   - Real-time metrics
   - Revenue tracking
   - Customer insights

---

**🎯 Ready to automate your spa business? Follow this guide and you'll have a fully functional AI-powered spa automation system running in no time!**
