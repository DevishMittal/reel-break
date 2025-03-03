# **ScreenBreak**

ScreenBreak is an AI-powered digital wellbeing assistant that monitors your short-form video consumption (YouTube Shorts, Instagram Reels, TikTok, etc.), provides insights into your usage patterns, and helps you manage your screen time with gentle interventions.

## **Features**
- **Platform Detection**: Automatically detects when you're using TikTok, YouTube Shorts, Instagram Reels, etc.
- **Usage Tracking**: Monitors how much time you spend on short-form video platforms
- **Smart Interventions**: Provides gentle, personalized reminders to take breaks
- **Usage Analytics**: See your patterns and progress over time
- **Customizable Goals**: Set daily limits and session restrictions

## **Getting Started**

### **Prerequisites**
- Python 3.8+
- [ScreenPipe](https://docs.screenpi.pe/docs/getting-started)
- Groq API key for LLM functionality

### **1) Clone the Repository**
```bash
git clone https://github.com/yourusername/ScreenBreak
cd ScreenBreak
```

### **2) Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3) Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4) Configure Environment Variables**
```bash
cp .env.example .env
```
Edit the `.env` file to add your Groq API key and configure other settings.

### **5) Run the FastAPI Server**
```bash
cd server
uvicorn main:app --reload
```

### **6) Run the ScreenPipe Client**
```bash
cd client
python main.py
```

## **How It Works**

1. **Detection**: The client monitors your screen through ScreenPipe's OCR capabilities
2. **Analysis**: The server uses Groq to identify when you're on short-form video platforms
3. **Tracking**: Your usage is tracked and stored locally in a SQLite database
4. **Intervention**: When you approach your usage limits, ScreenBreak sends gentle reminders
5. **Analytics**: View your usage patterns and progress through the API endpoints

## **Customization**

You can customize your experience by modifying these settings:
- Daily usage limits
- Session duration limits
- Intervention frequency (low, medium, high)

## **API Endpoints**

- **POST /process_screen**: Process screen content for platform detection
- **POST /update_settings**: Update user preferences
- **GET /usage_stats**: Get usage statistics for analytics

## **Future Enhancements**

- Web dashboard for statistics visualization
- Custom intervention strategies
- Weekly reports and insights
- Social accountability features