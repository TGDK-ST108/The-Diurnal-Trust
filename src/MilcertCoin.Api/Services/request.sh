curl -X POST "http://localhost:5000/program/execute-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "signedTransactionsBase64": [
      "BASE64_STEP_1",
      "BASE64_STEP_2",
      "BASE64_STEP_3"
    ],
    "simulateFirst": true,
    "haltOnError": true
  }'
