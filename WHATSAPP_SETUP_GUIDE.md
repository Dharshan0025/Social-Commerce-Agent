# WhatsApp Business API Setup Guide

## Issue Identified: Phone Number Allowlist

Your WhatsApp Business account is in **development mode** and can only send messages to pre-approved phone numbers. This is why messages aren't being sent.

## Error Details
```
(#131030) Recipient phone number not in allowed list
```

## Solution Steps

### 1. Add Test Phone Numbers (Development Mode)

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your app
3. Navigate to **WhatsApp > API Setup**
4. Find the **"To"** section
5. Click **"Manage"** next to phone numbers
6. Add your test phone numbers (including country code without +)
   - Format: `919876543210` (for India)
   - Add your own WhatsApp number first
   - Add any other numbers you want to test with

### 2. Verify Phone Numbers

1. After adding numbers, you'll receive verification codes
2. Enter the codes to verify each number
3. Only verified numbers can receive messages

### 3. Production Mode (Optional)

For production use:
1. Go to **WhatsApp > API Setup**
2. Submit your app for **Business Verification**
3. Once approved, you can send messages to any number
4. This process can take several days/weeks

## Current Status

✅ **Server**: Running correctly  
✅ **API Integration**: Code working properly  
✅ **Coordinator Flow**: Processing messages correctly  
❌ **Message Sending**: Blocked by phone number allowlist  

## Quick Fix for Testing

1. Add your phone number to the allowlist in Meta Business Manager
2. Update the test phone number in debug scripts to your actual number
3. Test again

## Alternative: Use WhatsApp Test Numbers

Meta provides test phone numbers for development:
- These don't require verification
- Check your WhatsApp Business API documentation for test numbers
- Usually in format: `15551234567`

## Next Steps

1. **Immediate**: Add your phone number to allowlist
2. **Short-term**: Test with verified numbers
3. **Long-term**: Apply for production access

The agent is working perfectly - it's just a WhatsApp Business account configuration issue!
