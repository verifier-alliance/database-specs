-- migrate:up

/*
  Make 'userdoc', 'devdoc' and 'storageLayout' optional in the compilation artifacts,
  because older solc versions do not output them.
  See https://github.com/argotorg/sourcify/issues/2296
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
            array ['userdoc', 'devdoc', 'storageLayout']
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
            array ['abi', 'userdoc', 'devdoc', 'sources', 'storageLayout'],
            array []::text[]
        ) AND
        validate_compilation_artifacts_abi(obj -> 'abi') AND
        validate_compilation_artifacts_sources(obj -> 'sources');
END;
$$ LANGUAGE plpgsql;
