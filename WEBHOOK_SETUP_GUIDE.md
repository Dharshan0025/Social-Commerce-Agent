# WhatsApp Webhook Setup Guide

## Problem Identified
Your server is running locally on `localhost:8000` but WhatsApp can't send webhooks to localhost. You need to expose your local server to the internet.

## Solution: Use ngrok

### Step 1: Install ngrok
1. Go to https://ngrok.com/download
2. Download ngrok for Windows
3. Extract the zip file
4. Move `ngrok.exe` to a folder in your PATH (or current directory)

### Step 2: Create ngrok account (optional but recommended)
1. Sign up at https://ngrok.com/
2. Get your auth token from dashboard
3. Run: `ngrok authtoken YOUR_AUTH_TOKEN`

### Step 3: Start your server
```bash
python main.py
```
Server should be running on `http://localhost:8000`

### Step 4: Expose server with ngrok
Open a new terminal and run:
```bash
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Account                       your-account
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL**: `https://abc123.ngrok.io`

### Step 5: Configure WhatsApp Webhook

1. Go to https://developers.facebook.com/
2. Select your app
3. Go to **WhatsApp > Configuration**
4. In **Webhook** section:
   - **Callback URL**: `https://abc123.ngrok.io/webhook/whatsapp`
   - **Verify Token**: `mytoken` (from your .env file)
   - Click **Verify and Save**

### Step 6: Subscribe to Webhook Events
1. In the same page, find **Webhook fields**
2. Subscribe to: `messages`
3. Click **Save**

### Step 7: Test Real WhatsApp Message
1. Send a WhatsApp message to your business number
2. Check your terminal - you should see webhook logs
3. Check ngrok web interface at http://127.0.0.1:4040 for request logs

## Troubleshooting

### Issue: Webhook verification fails
- Check that verify token matches exactly: `mytoken`
- Ensure ngrok URL is HTTPS (not HTTP)
- Make sure server is running on port 8000

### Issue: Messages not received
- Check webhook subscription is active
- Verify ngrok tunnel is running
- Check ngrok web interface for incoming requests
- Look for errors in server logs

### Issue: ngrok tunnel expires
- Free ngrok tunnels expire after 8 hours
- Restart ngrok and update webhook URL in Meta
- Consider ngrok paid plan for persistent URLs

## Production Deployment
For production, deploy to:
- Heroku
- Railway
- Render
- DigitalOcean
- AWS/GCP/Azure

## Current Status Check
Run this to verify everything is working:
```bash
python debug_whatsapp_flow.py
```
