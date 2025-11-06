-- migrate:up

ALTER TABLE compiled_contracts_sources
    ADD COLUMN created_at timestamptz NOT NULL DEFAULT NOW();

CREATE TRIGGER insert_set_created_at
    BEFORE INSERT ON compiled_contracts_sources
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_created_at();

CREATE TRIGGER update_reuse_created_at
    BEFORE UPDATE ON compiled_contracts_sources
    FOR EACH ROW
    EXECUTE FUNCTION trigger_reuse_created_at();

CREATE INDEX code_created_at ON code USING btree(created_at);
CREATE INDEX compiled_contracts_created_at ON compiled_contracts USING btree(created_at);
CREATE INDEX compiled_contracts_sources_created_at ON compiled_contracts_sources USING btree(created_at);
CREATE INDEX contract_deployments_created_at ON contract_deployments USING btree(created_at);
CREATE INDEX contracts_created_at ON contracts USING btree(created_at);
CREATE INDEX sources_created_at ON sources USING btree(created_at);
CREATE INDEX verified_contracts_created_at ON verified_contracts USING btree(created_at);

-- migrate:down

DROP INDEX IF EXISTS verified_contracts_created_at;
DROP INDEX IF EXISTS sources_created_at;
DROP INDEX IF EXISTS contracts_created_at;
DROP INDEX IF EXISTS contract_deployments_created_at;
DROP INDEX IF EXISTS compiled_contracts_sources_created_at;
DROP INDEX IF EXISTS compiled_contracts_created_at;
DROP INDEX IF EXISTS code_created_at;

DROP TRIGGER IF EXISTS update_reuse_created_at ON compiled_contracts_sources;
DROP TRIGGER IF EXISTS insert_set_created_at ON compiled_contracts_sources;

ALTER TABLE compiled_contracts_sources
    DROP COLUMN IF EXISTS created_at;
