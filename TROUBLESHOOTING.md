# Troubleshooting Guide

## SSL Certificate Verification Error

### Error Message
```json
{
    "error": "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1028)",
    "error_type": "server_error",
    "success": false
}
```

### Cause
This error occurs when Python cannot verify SSL certificates, commonly on macOS. It happens when the Flask backend tries to connect to Supabase or the AI microservice over HTTPS.

---

## Solutions (Try in Order)

### Solution 1: Install Python Certificates (Recommended for macOS)

Run the automated fix script:

```bash
chmod +x fix_ssl.sh
./fix_ssl.sh
```

Or manually:

1. **Find Python installation**:
   ```bash
   which python3
   ```

2. **Run Certificate Installer**:
   ```bash
   # For Python 3.11 (adjust version as needed)
   /Applications/Python\ 3.11/Install\ Certificates.command
   ```

3. **Restart your Flask server**

---

### Solution 2: Update Certificates Package

```bash
# Activate your virtual environment
source venv/bin/activate

# Update certifi
pip install --upgrade certifi

# Update pip and requests
pip install --upgrade pip requests urllib3
```

---

### Solution 3: Temporary SSL Bypass (Development Only)

**⚠️ WARNING: Only use this in local development, NEVER in production!**

Add to your `.env` file:
```env
VERIFY_SSL=false
```

Or set environment variable before running:
```bash
export VERIFY_SSL=false
python app.py
```

---

### Solution 4: Manual Certificate Installation

If you're using macOS:

```bash
# Install certificates via Python
pip install certifi

# Create symbolic link
python3 << EOF
import certifi
import os
import ssl

cert_path = certifi.where()
print(f"Certificate path: {cert_path}")
print(f"SSL version: {ssl.OPENSSL_VERSION}")
EOF
```

---

## Other Common Issues

### Issue: "SUPABASE_URL is required"

**Solution:**
1. Check if `.env` file exists
2. Verify `.env` contains `SUPABASE_URL` and `SUPABASE_KEY`
3. Ensure no extra spaces around `=` in `.env`

Example:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Issue: "Connection refused" to AI Microservice

**Solution:**
1. Check if AI microservice is running
2. Verify `AI_MICROSERVICE_URL` in `.env`
3. Test microservice directly:
   ```bash
   curl -X POST http://localhost:5001/api/chat \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"test"}]}'
   ```

---

### Issue: CORS Errors in React App

**Solution:**
1. Add your React app URL to `.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

2. Restart Flask server after changing `.env`

---

### Issue: "Company with this UUID already exists" (409)

**Cause:** React app tried to create a company with a UUID that already exists in the database.

**Solution:**
1. Generate a new UUID in React
2. Or delete the existing company:
   ```bash
   curl -X DELETE http://localhost:5000/api/companies/{uuid}
   ```

---

### Issue: Database Connection Failed

**Solution:**
1. Verify Supabase credentials:
   - Go to Supabase Dashboard → Settings → API
   - Copy URL and anon key
   - Update `.env` file

2. Check if schema is created:
   - Go to Supabase SQL Editor
   - Run `schema.sql` file

3. Test connection:
   ```python
   python3 -c "from database import get_db; print(get_db())"
   ```

---

### Issue: "Survey not found" when registering customer

**Solution:**
1. Verify survey exists:
   ```bash
   curl http://localhost:5000/api/surveys/{survey_uuid}
   ```

2. Check if survey is active:
   ```bash
   # Survey must have status='active'
   curl -X PUT http://localhost:5000/api/surveys/{survey_uuid} \
     -H "Content-Type: application/json" \
     -d '{"status":"active"}'
   ```

---

### Issue: Virtual Environment Not Activating

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

**If venv doesn't exist:**
```bash
python3 -m venv venv
```

---

### Issue: Port Already in Use

**Solution:**
1. Find process using port 5000:
   ```bash
   lsof -i :5000
   ```

2. Kill the process:
   ```bash
   kill -9 <PID>
   ```

3. Or use different port in `.env`:
   ```env
   FLASK_PORT=5001
   ```

---

## Debug Mode

Enable detailed logging:

```env
FLASK_ENV=development
```

Run with verbose output:
```bash
FLASK_DEBUG=1 python app.py
```

---

## Testing Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists with valid credentials
- [ ] Supabase schema created (`schema.sql`)
- [ ] Flask server running without errors
- [ ] Health check passes: `curl http://localhost:5000/health`
- [ ] Can create company with UUID
- [ ] AI microservice is accessible (if using chat)

---

## Getting Help

1. Check error response for `error_type`:
   - `validation_error` → Check request body format
   - `not_found` → Verify UUIDs exist
   - `duplicate_error` → UUID already in database
   - `database_error` → Check Supabase connection
   - `ai_service_error` → Check AI microservice

2. Review logs in terminal where Flask is running

3. Test endpoints individually with curl/Postman

---

## macOS Specific: SSL Certificate Installation

If the automated script doesn't work, try this:

```bash
# Install OpenSSL via Homebrew
brew install openssl

# Link certificates
export SSL_CERT_FILE=$(python3 -m certifi)
export REQUESTS_CA_BUNDLE=$(python3 -m certifi)

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export SSL_CERT_FILE=$(python3 -m certifi)' >> ~/.zshrc
echo 'export REQUESTS_CA_BUNDLE=$(python3 -m certifi)' >> ~/.zshrc
source ~/.zshrc

# Restart Flask server
```

---

## Still Having Issues?

1. Delete and recreate virtual environment:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Check Python version (requires 3.8+):
   ```bash
   python3 --version
   ```

3. Verify all files are present:
   ```bash
   ls -la
   # Should see: app.py, config.py, database.py, routes/, schema.sql, etc.
   ```

4. Test Supabase connection directly in Python:
   ```python
   python3
   >>> from supabase import create_client
   >>> client = create_client("YOUR_URL", "YOUR_KEY")
   >>> print(client)
   ```

