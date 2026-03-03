-- migrate:up

/*
  Add `additional_input` column to `compiled_contracts` to store compiler options
  that appear at the top level of standard JSON input but are not part of the `settings` field.
  Currently restricted to `storage_layout_overrides`, used by Vyper.
  See https://github.com/vyperlang/vyper/pull/4370
*/

CREATE OR REPLACE FUNCTION validate_additional_input(obj jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN obj IS NULL OR (
        is_jsonb_object(obj) AND
        validate_json_object_keys(
            obj,
            array []::text[],
            array ['storage_layout_overrides']
        )
    );
END;
$$ LANGUAGE plpgsql;

ALTER TABLE compiled_contracts
    ADD COLUMN additional_input jsonb;

ALTER TABLE compiled_contracts
    ADD CONSTRAINT additional_input_json_schema
    CHECK (validate_additional_input(additional_input));

-- migrate:down

ALTER TABLE compiled_contracts DROP CONSTRAINT IF EXISTS additional_input_json_schema;
ALTER TABLE compiled_contracts DROP COLUMN IF EXISTS additional_input;
DROP FUNCTION IF EXISTS validate_additional_input(jsonb);
