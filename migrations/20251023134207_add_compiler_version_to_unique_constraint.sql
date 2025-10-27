-- migrate:up
ALTER TABLE compiled_contracts
    DROP CONSTRAINT compiled_contracts_pseudo_pkey;

ALTER TABLE compiled_contracts
    ADD CONSTRAINT compiled_contracts_pseudo_pkey UNIQUE (compiler, version, language, creation_code_hash, runtime_code_hash);

-- migrate:down
ALTER TABLE compiled_contracts
    DROP CONSTRAINT compiled_contracts_pseudo_pkey;

ALTER TABLE compiled_contracts
    ADD CONSTRAINT compiled_contracts_pseudo_pkey UNIQUE (compiler, language, creation_code_hash, runtime_code_hash);
