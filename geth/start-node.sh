#!/usr/bin/env bash
set -euo pipefail

DATADIR="./data"
HTTP_ADDR="127.0.0.1"
HTTP_PORT="8545"
WS_PORT="8546"

geth init --datadir "$DATADIR" ./genesis.json

geth \
  --datadir "$DATADIR" \
  --networkid 31337 \
  --http \
  --http.addr "$HTTP_ADDR" \
  --http.port "$HTTP_PORT" \
  --http.api "admin,eth,net,web3,personal,txpool,debug" \
  --ws \
  --ws.addr "$HTTP_ADDR" \
  --ws.port "$WS_PORT" \
  --ws.api "admin,eth,net,web3,personal,txpool,debug" \
  --allow-insecure-unlock \
  --unlock "0xYOUR_SIGNER_ADDRESS" \
  --password ./password.txt \
  --mine \
  --syncmode full \
  --nodiscover
