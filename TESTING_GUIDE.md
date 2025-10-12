# AI Integration Testing Guide

This guide helps you test the complete AI integration flow for the survey system.

## Prerequisites

1. **Backend API running** on `http://localhost:8000`
2. **AI Microservice running** on:
   - `http://localhost:5001` (for `/api/start_session`)
   - `http://localhost:5000` (for `/api/chat`)
3. **Database migrated** with `session_id` and `metadata` columns
4. **Company and Survey created** in the database

## Quick Start

### 1. Apply Database Migration

If you have an existing database, run the migration:

```bash
# In Supabase SQL Editor or your PostgreSQL client
psql -f migrations/add_session_and_metadata.sql
```

Or manually:
```sql
ALTER TABLE customers ADD COLUMN session_id VARCHAR(255);
ALTER TABLE customers ADD COLUMN metadata JSONB DEFAULT '[]'::jsonb;
```

### 2. Create Test Data

```bash
# Create a company
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "comp-001",
    "name": "EV Motors Inc",
    "sector": "Electric Vehicles",
    "products": "Electric cars, batteries, charging stations",
    "details": "Leading manufacturer of electric vehicles"
  }'

# Create a survey
curl -X POST http://localhost:8000/api/companies/comp-001/surveys \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "survey-001",
    "title": "Product Feedback Survey",
    "description": "Gather customer insights about EV products"
  }'
```

## Testing Flow

### Test 1: Customer Registration + AI Session Start

```bash
curl -X POST http://localhost:8000/api/surveys/survey-001/customers \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "cust-001",
    "name": "John Doe",
    "age": 35,
    "gender": "Male"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "customer": {
      "uuid": "cust-001",
      "name": "John Doe",
      "age": 35,
      "gender": "Male",
      "session_id": "unique-session-id-here",
      "metadata": []
    },
    "ai_session": {
      "session_id": "unique-session-id-here",
      "initial_response": "What are the top workflows currently in place...",
      "status": 0
    },
    "survey": {...},
    "company": {...}
  },
  "message": "Customer registered successfully. Chat can now begin."
}
```

**Verify:**
- ✅ Customer created with `session_id` populated
- ✅ `metadata` is an empty array `[]`
- ✅ AI returned a first question
- ✅ Status is `0`

---

### Test 2: Chat Conversation (Status 0)

Use the session_id from the previous response.

```bash
curl -X POST http://localhost:8000/api/surveys/survey-001/customers/cust-001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Our main workflow is battery manufacturing and vehicle assembly."
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_message": {
      "uuid": "...",
      "message": "Our main workflow is battery manufacturing...",
      "sender": "user",
      "created_at": "..."
    },
    "ai_response": {
      "uuid": "...",
      "message": "Can you describe the primary bottleneck...",
      "sender": "ai",
      "created_at": "..."
    },
    "status": 0,
    "schema_completed": false,
    "session_id": "unique-session-id-here"
  }
}
```

**Verify:**
- ✅ User message stored
- ✅ AI response received
- ✅ Status is still `0` (schema not complete)
- ✅ `schema_completed` is `false`

---

### Test 3: Chat Conversation (Status 1 - Schema Complete)

Continue the conversation until the AI completes a schema:

```bash
curl -X POST http://localhost:8000/api/surveys/survey-001/customers/cust-001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The main bottleneck is battery testing, which happens weekly."
  }'
```

**Expected Response (when schema is complete):**
```json
{
  "success": true,
  "data": {
    "user_message": {...},
    "ai_response": {...},
    "status": 1,
    "schema_completed": true,
    "session_id": "unique-session-id-here",
    "comments": {
      "id": "domain_workflows",
      "current_top_workflows": ["Battery manufacturing", "Vehicle assembly"],
      "primary_bottleneck_description": "Battery testing",
      "bottleneck_occurrence_frequency": "weekly"
    }
  }
}
```

**Verify:**
- ✅ Status is `1`
- ✅ `schema_completed` is `true`
- ✅ `comments` contains the completed schema data
- ✅ Schema has `id` field (e.g., "domain_workflows")

---

### Test 4: Check Customer Metadata

```bash
curl -X GET http://localhost:8000/api/surveys/survey-001/customers/cust-001/metadata
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "customer_uuid": "cust-001",
    "customer_name": "John Doe",
    "session_id": "unique-session-id-here",
    "completed_schemas": [
      {
        "id": "domain_workflows",
        "current_top_workflows": ["Battery manufacturing", "Vehicle assembly"],
        "primary_bottleneck_description": "Battery testing",
        "bottleneck_occurrence_frequency": "weekly"
      }
    ],
    "total_completed": 1
  }
}
```

**Verify:**
- ✅ `completed_schemas` array contains the schema
- ✅ `total_completed` shows count (should be 1)
- ✅ Schema structure matches what was in `comments`

---

### Test 5: Continue Conversation (Next Schema)

After a schema is complete, the AI should move to the next topic:

```bash
curl -X POST http://localhost:8000/api/surveys/survey-001/customers/cust-001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Our biggest pain point is supply chain delays."
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_message": {...},
    "ai_response": {
      "message": "Can you estimate the impact in terms of time or cost..."
    },
    "status": 0,
    "schema_completed": false,
    "session_id": "unique-session-id-here"
  }
}
```

**Verify:**
- ✅ Status reset to `0` (new schema in progress)
- ✅ AI asking questions for next schema (e.g., "pain_points")
- ✅ Previous schema still saved in database

---

### Test 6: Check Multiple Completed Schemas

After completing 2+ schemas:

```bash
curl -X GET http://localhost:8000/api/surveys/survey-001/customers/cust-001/metadata
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "customer_uuid": "cust-001",
    "customer_name": "John Doe",
    "session_id": "unique-session-id-here",
    "completed_schemas": [
      {
        "id": "domain_workflows",
        "current_top_workflows": [...],
        ...
      },
      {
        "id": "pain_points",
        "top_pain_point_summary": "Supply chain delays",
        ...
      }
    ],
    "total_completed": 2
  }
}
```

**Verify:**
- ✅ Multiple schemas in array
- ✅ Schemas are in order of completion
- ✅ Each schema has unique `id`

---

### Test 7: Get Full Chat History

```bash
curl -X GET http://localhost:8000/api/surveys/survey-001/customers/cust-001/history
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "customer_uuid": "cust-001",
    "survey_uuid": "survey-001",
    "messages": [
      {
        "uuid": "...",
        "message": "Our main workflow is...",
        "sender": "user",
        "created_at": "..."
      },
      {
        "uuid": "...",
        "message": "Can you describe...",
        "sender": "ai",
        "created_at": "..."
      },
      ...
    ],
    "total_messages": 15
  }
}
```

**Verify:**
- ✅ All messages in chronological order
- ✅ Alternating user/ai messages
- ✅ Timestamps are correct

---

## Common Issues & Solutions

### Issue: "No AI session found for this customer"

**Cause:** Customer doesn't have a `session_id`

**Solution:**
```sql
-- Check if session_id column exists
SELECT session_id FROM customers WHERE uuid = 'cust-001';

-- If NULL, re-register the customer
```

### Issue: "Failed to start AI session: Connection refused"

**Cause:** AI microservice not running on port 5001

**Solution:**
```bash
# Check if AI service is running
curl http://localhost:5001/health

# Start the AI microservice
cd TF-ai
python run.py
```

### Issue: Metadata not updating when status=1

**Cause:** Database migration not applied or JSON parsing error

**Solution:**
```sql
-- Check if metadata column exists
SELECT metadata FROM customers WHERE uuid = 'cust-001';

-- If column doesn't exist, run migration
ALTER TABLE customers ADD COLUMN metadata JSONB DEFAULT '[]'::jsonb;
```

### Issue: Schema data missing in comments

**Cause:** AI microservice not returning proper response format

**Solution:** Check AI microservice logs and verify it's returning:
```json
{
  "response": "...",
  "status": 1,
  "comments": {...schema data...},
  "session_id": "..."
}
```

---

## Automated Test Script

Save as `test_ai_flow.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
SURVEY_UUID="survey-001"
CUSTOMER_UUID="test-$(date +%s)"

echo "Testing AI Integration Flow..."

# 1. Register customer
echo -e "\n1. Registering customer..."
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/api/surveys/$SURVEY_UUID/customers \
  -H "Content-Type: application/json" \
  -d "{
    \"uuid\": \"$CUSTOMER_UUID\",
    \"name\": \"Test User\",
    \"age\": 30,
    \"gender\": \"Other\"
  }")

echo "$REGISTER_RESPONSE" | jq .

SESSION_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.data.customer.session_id')
echo "Session ID: $SESSION_ID"

if [ "$SESSION_ID" = "null" ]; then
  echo "ERROR: Failed to get session_id"
  exit 1
fi

# 2. Send first message
echo -e "\n2. Sending first message..."
curl -s -X POST $BASE_URL/api/surveys/$SURVEY_UUID/customers/$CUSTOMER_UUID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Our workflows include production planning and quality control."
  }' | jq .

# 3. Check metadata
echo -e "\n3. Checking metadata..."
curl -s -X GET $BASE_URL/api/surveys/$SURVEY_UUID/customers/$CUSTOMER_UUID/metadata | jq .

echo -e "\nTest completed!"
```

Run with:
```bash
chmod +x test_ai_flow.sh
./test_ai_flow.sh
```

---

## Monitoring

### Check Database State

```sql
-- View all customers with session info
SELECT 
  uuid,
  name,
  session_id,
  jsonb_array_length(metadata) as completed_schemas_count,
  created_at
FROM customers;

-- View metadata for specific customer
SELECT 
  name,
  session_id,
  metadata
FROM customers 
WHERE uuid = 'cust-001';

-- Count messages per customer
SELECT 
  c.name,
  COUNT(cm.uuid) as message_count
FROM customers c
LEFT JOIN chat_messages cm ON c.uuid = cm.customer_uuid
GROUP BY c.uuid, c.name;
```

### Check AI Service Health

```bash
# Check start_session endpoint
curl http://localhost:5001/health

# Check chat endpoint
curl http://localhost:5000/health
```

---

## Success Criteria

A complete successful test should show:

1. ✅ Customer registered with `session_id`
2. ✅ Initial AI question received (status=0)
3. ✅ Multiple chat exchanges work
4. ✅ When status becomes 1, schema is saved to metadata
5. ✅ Metadata array grows with each completed schema
6. ✅ Session persists across multiple requests
7. ✅ Chat history is preserved
8. ✅ Same session_id used throughout

---

## Next Steps

After successful testing:

1. **Frontend Integration:** Build UI to display chat and track progress
2. **Progress Bar:** Show `completed_schemas / 11` as percentage
3. **Schema Validation:** Validate completed schemas against definitions
4. **Export:** Allow downloading completed schemas as JSON/CSV
5. **Analytics:** Aggregate insights across multiple customers

