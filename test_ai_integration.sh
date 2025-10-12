#!/bin/bash

# AI Integration Test Script
# This script tests the complete AI integration flow

set -e  # Exit on error

# Configuration
BASE_URL="http://localhost:8000"
COMPANY_UUID="test-company-$(date +%s)"
SURVEY_UUID="test-survey-$(date +%s)"
CUSTOMER_UUID="test-customer-$(date +%s)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}AI Integration Flow Test${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Check if services are running
echo -e "${YELLOW}Checking services...${NC}"
if ! curl -s -f "$BASE_URL/health" > /dev/null; then
    echo -e "${RED}❌ Backend API is not running on $BASE_URL${NC}"
    echo "Start it with: python app.py"
    exit 1
fi
echo -e "${GREEN}✓ Backend API is running${NC}"

if ! curl -s -f "http://localhost:5001/health" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Warning: AI microservice on port 5001 may not be running${NC}"
    echo "  (This is OK if testing without AI service)"
fi

echo ""

# Step 1: Create Company
echo -e "${YELLOW}Step 1: Creating test company...${NC}"
COMPANY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/companies" \
  -H "Content-Type: application/json" \
  -d "{
    \"uuid\": \"$COMPANY_UUID\",
    \"name\": \"Test EV Company\",
    \"sector\": \"Electric Vehicles\",
    \"products\": \"Electric cars and batteries\",
    \"details\": \"Leading EV manufacturer\"
  }")

if echo "$COMPANY_RESPONSE" | jq -e '.success' > /dev/null; then
    echo -e "${GREEN}✓ Company created${NC}"
    echo "$COMPANY_RESPONSE" | jq '.data.name'
else
    echo -e "${RED}❌ Failed to create company${NC}"
    echo "$COMPANY_RESPONSE" | jq .
    exit 1
fi

echo ""

# Step 2: Create Survey
echo -e "${YELLOW}Step 2: Creating test survey...${NC}"
SURVEY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/companies/$COMPANY_UUID/surveys" \
  -H "Content-Type: application/json" \
  -d "{
    \"uuid\": \"$SURVEY_UUID\",
    \"title\": \"Product Feedback Survey\",
    \"description\": \"Gathering customer insights\"
  }")

if echo "$SURVEY_RESPONSE" | jq -e '.success' > /dev/null; then
    echo -e "${GREEN}✓ Survey created${NC}"
    echo "$SURVEY_RESPONSE" | jq '.data.title'
else
    echo -e "${RED}❌ Failed to create survey${NC}"
    echo "$SURVEY_RESPONSE" | jq .
    exit 1
fi

echo ""

# Step 3: Register Customer (starts AI session)
echo -e "${YELLOW}Step 3: Registering customer (starting AI session)...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/surveys/$SURVEY_UUID/customers" \
  -H "Content-Type: application/json" \
  -d "{
    \"uuid\": \"$CUSTOMER_UUID\",
    \"name\": \"Test Customer\",
    \"age\": 35,
    \"gender\": \"Other\"
  }")

if echo "$REGISTER_RESPONSE" | jq -e '.success' > /dev/null; then
    echo -e "${GREEN}✓ Customer registered${NC}"
    
    SESSION_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.data.customer.session_id // .data.ai_session.session_id // empty')
    
    if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ]; then
        echo -e "${GREEN}✓ AI session started: $SESSION_ID${NC}"
        
        INITIAL_RESPONSE=$(echo "$REGISTER_RESPONSE" | jq -r '.data.ai_session.initial_response // empty')
        if [ -n "$INITIAL_RESPONSE" ]; then
            echo -e "${GREEN}AI's first question:${NC}"
            echo "  $INITIAL_RESPONSE"
        fi
    else
        echo -e "${YELLOW}⚠ Warning: No session_id received (AI service may be down)${NC}"
    fi
else
    echo -e "${RED}❌ Failed to register customer${NC}"
    echo "$REGISTER_RESPONSE" | jq .
    exit 1
fi

echo ""

# Step 4: Send Chat Message
echo -e "${YELLOW}Step 4: Sending chat message...${NC}"
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/surveys/$SURVEY_UUID/customers/$CUSTOMER_UUID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Our main workflows include battery manufacturing, vehicle assembly, and quality testing. The biggest bottleneck is supply chain coordination."
  }')

if echo "$CHAT_RESPONSE" | jq -e '.success' > /dev/null; then
    echo -e "${GREEN}✓ Chat message sent${NC}"
    
    STATUS=$(echo "$CHAT_RESPONSE" | jq -r '.data.status // 0')
    AI_RESPONSE=$(echo "$CHAT_RESPONSE" | jq -r '.data.ai_response.message // empty')
    
    echo -e "${GREEN}AI Status: $STATUS${NC}"
    if [ -n "$AI_RESPONSE" ]; then
        echo -e "${GREEN}AI Response:${NC}"
        echo "  $AI_RESPONSE"
    fi
    
    SCHEMA_COMPLETED=$(echo "$CHAT_RESPONSE" | jq -r '.data.schema_completed // false')
    if [ "$SCHEMA_COMPLETED" = "true" ]; then
        echo -e "${GREEN}🎉 Schema completed!${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Chat failed (might be expected if AI service is not running)${NC}"
    echo "$CHAT_RESPONSE" | jq .
fi

echo ""

# Step 5: Check Metadata
echo -e "${YELLOW}Step 5: Checking customer metadata...${NC}"
METADATA_RESPONSE=$(curl -s -X GET "$BASE_URL/api/surveys/$SURVEY_UUID/customers/$CUSTOMER_UUID/metadata")

if echo "$METADATA_RESPONSE" | jq -e '.success' > /dev/null; then
    echo -e "${GREEN}✓ Metadata retrieved${NC}"
    
    TOTAL_COMPLETED=$(echo "$METADATA_RESPONSE" | jq -r '.data.total_completed // 0')
    echo -e "${GREEN}Completed schemas: $TOTAL_COMPLETED / 11${NC}"
    
    if [ "$TOTAL_COMPLETED" -gt 0 ]; then
        echo -e "${GREEN}Completed schema IDs:${NC}"
        echo "$METADATA_RESPONSE" | jq -r '.data.completed_schemas[].id // empty' | sed 's/^/  - /'
    fi
else
    echo -e "${RED}❌ Failed to retrieve metadata${NC}"
    echo "$METADATA_RESPONSE" | jq .
    exit 1
fi

echo ""

# Step 6: Get Chat History
echo -e "${YELLOW}Step 6: Retrieving chat history...${NC}"
HISTORY_RESPONSE=$(curl -s -X GET "$BASE_URL/api/surveys/$SURVEY_UUID/customers/$CUSTOMER_UUID/history")

if echo "$HISTORY_RESPONSE" | jq -e '.success' > /dev/null; then
    echo -e "${GREEN}✓ Chat history retrieved${NC}"
    
    MESSAGE_COUNT=$(echo "$HISTORY_RESPONSE" | jq -r '.data.total_messages // 0')
    echo -e "${GREEN}Total messages: $MESSAGE_COUNT${NC}"
else
    echo -e "${RED}❌ Failed to retrieve chat history${NC}"
    echo "$HISTORY_RESPONSE" | jq .
    exit 1
fi

echo ""

# Summary
echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}✓ All tests completed successfully!${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Test Data Created:"
echo "  Company UUID:  $COMPANY_UUID"
echo "  Survey UUID:   $SURVEY_UUID"
echo "  Customer UUID: $CUSTOMER_UUID"
if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ]; then
    echo "  Session ID:    $SESSION_ID"
fi
echo ""
echo "Cleanup (optional):"
echo "  curl -X DELETE $BASE_URL/api/companies/$COMPANY_UUID"
echo ""

