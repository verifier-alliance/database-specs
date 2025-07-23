-- migrate:up
CREATE INDEX IF NOT EXISTS contract_deployments_address ON contract_deployments USING btree(address);

-- migrate:down
DROP INDEX IF EXISTS contract_deployments_address;
