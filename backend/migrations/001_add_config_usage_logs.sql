CREATE TABLE IF NOT EXISTS config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_name VARCHAR(64) NOT NULL,
  provider_name VARCHAR(32) NOT NULL,
  base_url VARCHAR(255) NOT NULL,
  model_id VARCHAR(128) NOT NULL,
  api_key_encrypted VARCHAR(512) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  notes VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS usage_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_name VARCHAR(64) NOT NULL,
  provider_name VARCHAR(32) NOT NULL,
  model_id VARCHAR(128) NOT NULL,
  tokens_input INTEGER NOT NULL,
  tokens_output INTEGER NOT NULL,
  cost_estimate FLOAT NOT NULL,
  request_path VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL
);
