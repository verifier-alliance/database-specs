-- migrate:up

/*
  Allow storing the new compiler output field `transientStorageLayout`.
*/

CREATE OR REPLACE FUNCTION validate_compilation_artifacts(obj jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN
        is_jsonb_object(obj) AND
        validate_json_object_keys(
            obj,
            array ['abi', 'sources'],
            array ['userdoc', 'devdoc', 'storageLayout', 'transientStorageLayout']
        ) AND
        validate_compilation_artifacts_abi(obj -> 'abi') AND
        validate_compilation_artifacts_sources(obj -> 'sources');
END;
$$ LANGUAGE plpgsql;

-- migrate:down

CREATE OR REPLACE FUNCTION validate_compilation_artifacts(obj jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN
        is_jsonb_object(obj) AND
        validate_json_object_keys(
            obj,
            array ['abi', 'sources'],
            array ['userdoc', 'devdoc', 'storageLayout']
        ) AND
        validate_compilation_artifacts_abi(obj -> 'abi') AND
        validate_compilation_artifacts_sources(obj -> 'sources');
END;
$$ LANGUAGE plpgsql;
