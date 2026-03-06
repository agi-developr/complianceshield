#!/bin/bash
# ComplianceShield - Restart All Services
# Run this tomorrow morning to get everything back up

echo "Starting ComplianceShield services..."

cd ~/hackathon-compliance/agents/seller-simple-agent

echo "[1/4] Starting A2A Seller Agent (port 9000)..."
poetry run python -m src.agent_a2a --port 9000 --buyer-url http://localhost:8000 &
sleep 3

echo "[2/4] Starting MCP Server (port 3000)..."
poetry run python -c "from src.mcp_server import main; main()" &
sleep 2

echo "[3/4] Starting Web Demo (port 8080)..."
poetry run python -c "from src.web_demo import main; main()" &
sleep 2

cd ~/hackathon-compliance/agents/buyer-simple-agent

echo "[4/4] Starting Buyer Agent (port 8000)..."
poetry run python -m src.web &
sleep 2

echo ""
echo "All services started! Checking health..."
sleep 3

for port in 8080 9000 3000 8000; do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port)
  if [ "$code" = "200" ]; then
    echo "  Port $port: OK"
  else
    echo "  Port $port: FAILED ($code)"
  fi
done

echo ""
echo "Start ngrok separately: ngrok http 9000"
echo "Then update Ideas Board with new ngrok URL"
