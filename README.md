# Social Commerce AI Agent

A comprehensive SaaS backend that automates product enquiries and orders via WhatsApp using CrewAI agents and Groq LLM. This system provides intelligent, multilingual customer support for social commerce platforms.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized CrewAI agents for product extraction, inventory matching, response generation, and logging
- **Multilingual Support**: English, Tamil, Telugu, Malayalam, Kannada, Hindi, and mixed languages (Thanglish, Hinglish)
- **Multi-Modal Processing**: Text, image (OCR), and audio (ASR) message support
- **Real-time Inventory**: Google Sheets integration for inventory and order management
- **WhatsApp Integration**: Complete webhook handling for WhatsApp Business API
- **Payment Processing**: Payment gateway webhook support
- **Intelligent Matching**: AI-powered product matching with similarity scoring
- **Conversation Flow**: Multi-step purchase flows with address collection
- **Comprehensive Logging**: Detailed interaction and order tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   FastAPI        │    │   CrewAI        │
│   Webhook       │───▶│   Server         │───▶│   Agents        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Payment       │    │   Google         │    │   Groq LLM      │
│   Gateway       │───▶│   Sheets         │◀───│   API           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Agent Pipeline

1. **Product Extractor Agent**: Extracts structured product information from customer messages
2. **Inventory Matcher Agent**: Matches extracted info with Google Sheets inventory
3. **Response Generator Agent**: Creates natural, multilingual responses
4. **Logger Agent**: Records all interactions and orders
5. **Coordinator Agent**: Orchestrates the entire pipeline and manages conversation flows

## 📋 Prerequisites

- Python 3.8+
- Groq API account and API key
- Google Cloud Platform account with Sheets API enabled
- WhatsApp Business API access
- Payment gateway account (optional)
- HuggingFace account (optional, for image/audio processing)

## 🛠️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd social-commerce-agent
pip install -r requirements.txt
```

### 2. Groq API Setup

1. Visit [Groq Console](https://console.groq.com/)
2. Create an account and generate an API key
3. Note down your API key for environment configuration

### 3. Google Sheets Setup

#### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

4. Create Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in service account details
   - Click "Create and Continue"

5. Generate Key:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON" format
   - Download the JSON file

#### Setup Google Sheets

1. Create a new Google Sheet
2. Create two worksheets:
   - **Inventory**: For product catalog
   - **Leads & Orders**: For customer interactions (auto-created)

3. Setup Inventory sheet with columns:
   ```
   Vendor_Code | Product_Name | Brand | Type | Style | Color | Size | Sale_Price | Qty_On_Hand | Payment_Link
   ```

4. Share the sheet with your service account email (found in the JSON file)

5. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
   ```

### 4. WhatsApp Business API Setup

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app and select "Business"
3. Add WhatsApp product to your app
4. Get your:
   - Phone Number ID
   - Access Token
   - Verify Token (create your own)

5. Configure webhook URL: `https://your-domain.com/webhook/whatsapp`

### 5. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Fill in your configuration:
   ```env
   # Groq API Configuration
   GROQ_API_KEY=your_groq_api_key_here
   
   # Google Sheets Configuration
   GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/your/service-account-key.json
   INVENTORY_SHEET_ID=your_google_sheet_id_here
   INVENTORY_SHEET_NAME=Inventory
   LEADS_SHEET_NAME=Leads & Orders
   
   # WhatsApp Configuration
   WHATSAPP_VERIFY_TOKEN=your_whatsapp_verify_token
   WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
   
   # Payment Gateway Configuration (Optional)
   PAYMENT_SECRET=your_payment_gateway_secret
   
   # HuggingFace Configuration (Optional)
   HUGGINGFACE_API_TOKEN=your_huggingface_token
   
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=true
   ```

### 6. Sample Inventory Data

Add sample products to your Inventory sheet:

| Vendor_Code | Product_Name | Brand | Type | Style | Color | Size | Sale_Price | Qty_On_Hand | Payment_Link |
|-------------|--------------|-------|------|-------|-------|------|------------|-------------|--------------|
| VS001 | Cotton Casual Shirt | BrandA | shirt | casual | blue | M | 599 | 15 | https://pay.example.com/VS001 |
| VS002 | Silk Saree | BrandB | saree | silk | red | OneSize | 2999 | 8 | https://pay.example.com/VS002 |
| VS003 | Denim Jeans | BrandC | jeans | casual | black | L | 1299 | 12 | https://pay.example.com/VS003 |

## 🚀 Running the Application

### Local Development

```bash
# Run the server
python main.py

# Or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

### API Endpoints

- `GET /health` - Health check
- `GET /webhook/whatsapp` - WhatsApp webhook verification
- `POST /webhook/whatsapp` - WhatsApp message processing
- `POST /webhook/payment` - Payment webhook processing
- `POST /test/message` - Test endpoint (debug mode only)

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_integration.py -v
```

### Manual Testing

#### Test WhatsApp Webhook

```bash
curl -X POST http://localhost:8000/test/message \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "919876543210",
            "id": "test123",
            "timestamp": "1694876543",
            "type": "text",
            "text": {
              "body": "I want a blue shirt in medium size"
            }
          }],
          "contacts": [{
            "profile": {
              "name": "Test User"
            }
          }]
        }
      }]
    }]
  }'
```

#### Test Payment Webhook

```bash
curl -X POST http://localhost:8000/webhook/payment \
  -H "Content-Type: application/json" \
  -d '{
    "status": "success",
    "payment_id": "pay_test123",
    "customer_phone": "919876543210",
    "amount": "599.00"
  }'
```

## 📱 Sample WhatsApp Messages

### English Messages
- "I want a blue shirt in medium size"
- "VS001 buy now"
- "Show me red sarees"
- "Order 2 black jeans size L"

### Tamil Messages
- "நீல நிற சட்டை வேணும் medium size"
- "VS001 வாங்கணும்"
- "சிவப்பு புடவை காட்டுங்க"

### Thanglish Messages
- "Blue shirt M size venum"
- "VS001 product buy pannanum"
- "Red saree irukka?"

### Hindi Messages
- "नीली शर्ट चाहिए medium size में"
- "VS001 खरीदना है"
- "लाल साड़ी दिखाइए"

## 🌐 Deployment

### Deploy to Render

1. Create account on [Render](https://render.com/)
2. Connect your GitHub repository
3. Create a new Web Service
4. Configure environment variables
5. Deploy

### Deploy to Railway

1. Create account on [Railway](https://railway.app/)
2. Connect your GitHub repository
3. Add environment variables
4. Deploy

### Deploy to Heroku

1. Install Heroku CLI
2. Create Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Set environment variables:
   ```bash
   heroku config:set GROQ_API_KEY=your_key
   heroku config:set INVENTORY_SHEET_ID=your_sheet_id
   # ... add all other variables
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

## 🔧 Configuration

### Agent Prompts Customization

Each agent has customizable system prompts in their respective files:

- `agents/product_extractor.py` - Product extraction prompts
- `agents/inventory_matcher.py` - Inventory matching logic
- `agents/response_generator.py` - Response generation prompts

### Language Support

The system supports multiple languages and can be extended by:

1. Adding language-specific examples in agent prompts
2. Updating the language detection logic
3. Adding cultural context for better responses

### Inventory Schema

Customize the inventory schema by modifying:
- Google Sheets column structure
- `utils/google_sheets.py` search logic
- Agent prompts to match your product attributes

## 📊 Monitoring and Logging

### Logs

The application uses structured logging:
- Request/response logs
- Agent processing logs
- Error tracking
- Performance metrics

### Sentry Integration

Optional Sentry integration for error tracking:
```env
SENTRY_DSN=your_sentry_dsn_here
```

### Google Sheets Analytics

All interactions are logged to Google Sheets for:
- Customer behavior analysis
- Product demand tracking
- Conversion rate monitoring
- Multi-language usage patterns

## 🔒 Security

- Webhook signature verification
- Environment variable protection
- Input validation and sanitization
- Rate limiting (implement as needed)
- HTTPS enforcement in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section below

## 🔧 Troubleshooting

### Common Issues

1. **Google Sheets Permission Error**
   - Ensure service account has access to the sheet
   - Check credentials file path
   - Verify API is enabled

2. **Groq API Errors**
   - Check API key validity
   - Verify rate limits
   - Check model availability

3. **WhatsApp Webhook Issues**
   - Verify webhook URL is accessible
   - Check verify token matches
   - Ensure HTTPS in production

4. **Import Errors**
   - Check all dependencies are installed
   - Verify Python version compatibility
   - Check file paths and structure

### Debug Mode

Enable debug mode for detailed logging:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Health Checks

Monitor application health:
```bash
curl http://localhost:8000/health
```

## 📈 Performance Optimization

- Use async/await for I/O operations
- Implement caching for frequent queries
- Optimize Google Sheets queries
- Use connection pooling
- Monitor response times

## 🔮 Future Enhancements

- Voice message support
- Image product recognition
- Chatbot personality customization
- Advanced analytics dashboard
- Multi-tenant support
- Automated testing pipeline
- Performance monitoring
- A/B testing framework
