#!/bin/bash

# Swatantra Backend API Testing Guide
# This script demonstrates how to test the backend API

BASE_URL="http://localhost:8000"

echo "🧪 Swatantra Backend API Testing Guide"
echo "======================================"
echo ""
echo "Prerequisites:"
echo "  - Backend running on $BASE_URL"
echo "  - jq installed (for pretty JSON output): brew/apt install jq"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Helper function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${BLUE}TEST: $description${NC}"
    echo "Command:"
    
    if [ -z "$data" ]; then
        echo "curl -X $method $BASE_URL$endpoint"
        curl -s -X $method "$BASE_URL$endpoint" | jq . 2>/dev/null || curl -s -X $method "$BASE_URL$endpoint"
    else
        echo "curl -X $method $BASE_URL$endpoint \\"
        echo "  -H 'Content-Type: application/json' \\"
        echo "  -d '$data'"
        curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" | jq . 2>/dev/null || curl -s -X $method "$BASE_URL$endpoint" -H "Content-Type: application/json" -d "$data"
    fi
    
    echo -e "${GREEN}✓${NC}"
    echo ""
}

# 1. Health Check
echo -e "${YELLOW}1. Health Check${NC}"
test_endpoint "GET" "/api/health" "" "Check backend health"

# 2. Get Configuration
echo -e "${YELLOW}2. System Configuration${NC}"
test_endpoint "GET" "/api/config" "" "Get system configuration"

# 3. Create an Agent
echo -e "${YELLOW}3. Create an Agent${NC}"
AGENT_DATA='{
  "name": "DocumentAnalyzer",
  "description": "Analyzes documents and extracts insights",
  "agent_type": "reasoning",
  "tools": ["document_processor", "web_search"]
}'
test_endpoint "POST" "/api/agents" "$AGENT_DATA" "Create a new agent"

# Extract agent ID from previous response (in real script, parse JSON)
AGENT_ID=1

# 4. List All Agents
echo -e "${YELLOW}4. List Agents${NC}"
test_endpoint "GET" "/api/agents" "" "List all agents"

# 5. Get Specific Agent
echo -e "${YELLOW}5. Get Agent Details${NC}"
test_endpoint "GET" "/api/agents/$AGENT_ID" "" "Get agent details"

# 6. Create a Task
echo -e "${YELLOW}6. Create a Task${NC}"
TASK_DATA='{
  "agent_id": 1,
  "title": "Analyze Annual Report",
  "description": "Analyze the company annual report",
  "objective": "Summarize the annual report and extract key financial metrics",
  "priority": 5,
  "input_data": {
    "report_url": "https://example.com/annual-report.pdf"
  }
}'
test_endpoint "POST" "/api/tasks" "$TASK_DATA" "Create a new task"

TASK_ID=1

# 7. List Tasks
echo -e "${YELLOW}7. List Tasks${NC}"
test_endpoint "GET" "/api/tasks" "" "List all tasks"

# 8. Get Task Details
echo -e "${YELLOW}8. Get Task Details${NC}"
test_endpoint "GET" "/api/tasks/$TASK_ID" "" "Get specific task"

# 9. Execute Task
echo -e "${YELLOW}9. Execute Task${NC}"
test_endpoint "POST" "/api/tasks/$TASK_ID/execute" "" "Execute task"

# 10. Get Analytics Summary
echo -e "${YELLOW}10. Analytics Summary${NC}"
test_endpoint "GET" "/api/analytics/summary" "" "Get analytics summary"

# 11. Get Agent Performance
echo -e "${YELLOW}11. Agent Performance${NC}"
test_endpoint "GET" "/api/analytics/agents/performance" "" "Get agent performance metrics"

# 12. Get Task Distribution
echo -e "${YELLOW}12. Task Distribution${NC}"
test_endpoint "GET" "/api/analytics/tasks/distribution" "" "Get task status distribution"

# 13. Check Offline Sync Status
echo -e "${YELLOW}13. Offline Sync Status${NC}"
test_endpoint "GET" "/api/sync-status" "" "Check offline sync status"

# 14. Get Available Tools
echo -e "${YELLOW}14. Available Tools${NC}"
test_endpoint "GET" "/api/metrics/available-tools" "" "Get available tools for agents"

# 15. Update Agent
echo -e "${YELLOW}15. Update Agent${NC}"
UPDATE_DATA='{
  "description": "Advanced document analyzer with tool support"
}'
test_endpoint "PUT" "/api/agents/$AGENT_ID" "$UPDATE_DATA" "Update agent"

# 16. Activate Agent
echo -e "${YELLOW}16. Activate Agent${NC}"
test_endpoint "POST" "/api/agents/$AGENT_ID/activate" "" "Activate agent"

# 17. Cancel Task
echo -e "${YELLOW}17. Cancel Task${NC}"
test_endpoint "POST" "/api/tasks/$TASK_ID/cancel" "" "Cancel task (if pending)"

# 18. Delete Agent
echo -e "${YELLOW}18. Delete Agent${NC}"
test_endpoint "DELETE" "/api/agents/$AGENT_ID" "" "Delete agent (be careful!)"

echo ""
echo -e "${GREEN}✅ Testing Complete!${NC}"
echo ""
echo "📚 Interactive API Documentation:"
echo "  - Swagger UI: $BASE_URL/docs"
echo "  - ReDoc: $BASE_URL/redoc"
echo ""
echo "💡 Tips:"
echo "  - Use curl with -v flag for verbose output including headers"
echo "  - Use jq for pretty-printing JSON: pipe output to jq"
echo "  - For POST/PUT requests, use @filename to read JSON from file"
echo ""
