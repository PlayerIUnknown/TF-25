#!/bin/bash

# Test script for AI Summary Endpoint
# Usage: ./test_ai_summary.sh <survey_uuid>

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
SURVEY_UUID="${1:-}"

if [ -z "$SURVEY_UUID" ]; then
    echo -e "${RED}Error: Survey UUID is required${NC}"
    echo "Usage: $0 <survey_uuid>"
    exit 1
fi

echo -e "${BLUE}=== Testing AI Summary Endpoint ===${NC}\n"

# Test 1: Get AI Summary
echo -e "${GREEN}Test 1: Fetching AI Summary...${NC}"
RESPONSE=$(curl -s -X GET "${BASE_URL}/api/surveys/${SURVEY_UUID}/ai-summary" \
  -H "Content-Type: application/json")

# Check if response is valid JSON
if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
    echo -e "${RED}Error: Invalid JSON response${NC}"
    echo "$RESPONSE"
    exit 1
fi

# Check if request was successful
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
if [ "$SUCCESS" != "true" ]; then
    echo -e "${RED}Error: Request failed${NC}"
    echo "$RESPONSE" | jq '.'
    exit 1
fi

echo -e "${GREEN}✓ AI Summary fetched successfully!${NC}\n"

# Display key metrics
echo -e "${BLUE}=== Key Metrics ===${NC}"
echo "$RESPONSE" | jq '.data.summary | {
  total_participants,
  completed_surveys,
  in_progress_surveys,
  completion_rate_percentage,
  positive_indicators,
  negative_indicators
}'

# Display top keywords
echo -e "\n${BLUE}=== Top Keywords ===${NC}"
echo "$RESPONSE" | jq -r '.data.summary.top_keywords[]' | nl

# Display key pain points
echo -e "\n${BLUE}=== Key Pain Points ===${NC}"
echo "$RESPONSE" | jq -r '.data.summary.key_pain_points[]' | nl

# Display key insights
echo -e "\n${BLUE}=== Key Insights ===${NC}"
echo "$RESPONSE" | jq -r '.data.summary.key_insights'

# Display recommendations
echo -e "\n${BLUE}=== Recommendations ===${NC}"
echo "$RESPONSE" | jq -r '.data.summary.recommendations'

# Save full response to file
OUTPUT_FILE="ai_summary_${SURVEY_UUID}_$(date +%Y%m%d_%H%M%S).json"
echo "$RESPONSE" | jq '.' > "$OUTPUT_FILE"
echo -e "\n${GREEN}✓ Full response saved to: ${OUTPUT_FILE}${NC}"

# Test 2: Compare with basic stats
echo -e "\n${BLUE}=== Comparing with Basic Stats ===${NC}"
STATS_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/surveys/${SURVEY_UUID}/stats" \
  -H "Content-Type: application/json")

echo "Basic Stats:"
echo "$STATS_RESPONSE" | jq '.data'

echo -e "\n${GREEN}=== Test Complete ===${NC}"

