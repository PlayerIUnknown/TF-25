# Gunicorn Deployment Guide

This guide explains how to run the TF-25 backend with Gunicorn in production.

## Quick Start

### 1. Basic Gunicorn Command

```bash
# Simple command
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4

# With configuration file
gunicorn --config gunicorn_config.py wsgi:app
```

### 2. Using the Start Script

```bash
# Make script executable (first time only)
chmod +x start_gunicorn.sh

# Run the script
./start_gunicorn.sh
```

### 3. With Custom Settings

```bash
# Set environment variables
export FLASK_PORT=8000
export WORKERS=4

# Run
./start_gunicorn.sh
```

## Production Deployment with systemd

### 1. Edit the Service File

Update `tf25-backend.service` with your actual paths:

```bash
# Replace these values:
User=your-username                          # Your Linux username
Group=your-username                         # Your Linux group
WorkingDirectory=/path/to/TF-25             # Full path to project
Environment="PATH=/path/to/TF-25/venv/bin"  # Full path to venv
EnvironmentFile=/path/to/TF-25/.env         # Full path to .env file
ExecStart=/path/to/TF-25/venv/bin/gunicorn --config gunicorn_config.py wsgi:app
```

### 2. Install the Service

```bash
# Copy service file to systemd directory
sudo cp tf25-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tf25-backend

# Start the service
sudo systemctl start tf25-backend
```

### 3. Manage the Service

```bash
# Check status
sudo systemctl status tf25-backend

# View logs
sudo journalctl -u tf25-backend -f

# Restart service
sudo systemctl restart tf25-backend

# Stop service
sudo systemctl stop tf25-backend
```

## Configuration Options

### Workers

The number of workers should be `(2 x CPU_cores) + 1`. Adjust in `gunicorn_config.py`:

```python
workers = 4  # For a 2-core machine
```

Or set via environment variable:

```bash
export WORKERS=4
```

### Timeout

Default is 120 seconds. Increase if you have long-running requests:

```python
timeout = 180  # In gunicorn_config.py
```

### Port

Set via environment variable:

```bash
export FLASK_PORT=8000
```

Or in `.env` file:

```env
FLASK_PORT=8000
```

## Running Behind Nginx (Recommended)

### Nginx Configuration

Create `/etc/nginx/sites-available/tf25-backend`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/tf25-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring and Logs

### Real-time Logs

```bash
# Application logs
sudo journalctl -u tf25-backend -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Survey Backend",
  "version": "1.0.0"
}
```

## GCP-Specific Deployment

### 1. Install Dependencies

```bash
cd /path/to/TF-25

# Activate virtual environment
source venv/bin/activate

# Install/upgrade packages
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Create .env file
cat > .env << EOF
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
AI_MICROSERVICE_URL=http://localhost:5001/api/chat
GROQ_API_KEY=your_groq_api_key
FLASK_PORT=8000
FLASK_ENV=production
CORS_ORIGINS=https://your-frontend.com
EOF
```

### 3. Test Run

```bash
# Test with Gunicorn
./start_gunicorn.sh

# Or manually
gunicorn --config gunicorn_config.py wsgi:app
```

### 4. Setup Firewall

```bash
# Allow HTTP traffic
sudo ufw allow 8000/tcp

# Or if behind nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Permission Denied

```bash
# Make scripts executable
chmod +x start_gunicorn.sh

# Check file permissions
ls -la
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### SSL/Certificate Issues

The application has SSL verification disabled for development. For production, review SSL settings in `app.py` and consider enabling proper certificate verification.

## Performance Tuning

### Worker Class

For I/O-bound applications:

```python
worker_class = 'gevent'  # Requires: pip install gevent
workers = 2
```

### Keep-Alive

```python
keepalive = 5  # Seconds to wait for requests on a Keep-Alive connection
```

### Max Requests

Restart workers after handling N requests (prevents memory leaks):

```python
max_requests = 1000
max_requests_jitter = 50
```

## Security Recommendations

1. **Use HTTPS**: Set up SSL certificates (Let's Encrypt)
2. **Firewall**: Only expose necessary ports
3. **Environment Variables**: Never commit `.env` file
4. **Update Dependencies**: Regularly update packages
5. **Rate Limiting**: Implement rate limiting for APIs
6. **Monitoring**: Set up logging and monitoring tools

## Quick Commands Reference

```bash
# Start with script
./start_gunicorn.sh

# Start with config file
gunicorn --config gunicorn_config.py wsgi:app

# Start with custom workers
gunicorn wsgi:app --workers 4 --bind 0.0.0.0:8000

# Start in background
nohup gunicorn --config gunicorn_config.py wsgi:app > gunicorn.log 2>&1 &

# Stop background process
pkill -f gunicorn

# Check if running
ps aux | grep gunicorn
```

