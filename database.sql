SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: is_jsonb_array(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_jsonb_array(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        jsonb_typeof(obj) = 'array';
END;
$$;


--
-- Name: is_jsonb_null(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_jsonb_null(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        jsonb_typeof(obj) = 'null';
END;
$$;


--
-- Name: is_jsonb_number(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_jsonb_number(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        jsonb_typeof(obj) = 'number';
END;
$$;


--
-- Name: is_jsonb_object(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_jsonb_object(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        jsonb_typeof(obj) = 'object';
END;
$$;


--
-- Name: is_jsonb_string(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_jsonb_string(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        jsonb_typeof(obj) = 'string';
END;
$$;


--
-- Name: is_valid_hex(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_valid_hex(val text, repetition text) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN val SIMILAR TO CONCAT('0x([0-9|a-f|A-F][0-9|a-f|A-F])', repetition);
END;
$$;


--
-- Name: trigger_reuse_created_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.trigger_reuse_created_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.created_at = OLD.created_at;
    RETURN NEW;
END;
$$;


--
-- Name: trigger_reuse_created_by(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.trigger_reuse_created_by() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.created_by = OLD.created_by;
    RETURN NEW;
END;
$$;


--
-- Name: trigger_set_created_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.trigger_set_created_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.created_at = NOW();
    RETURN NEW;
END;
$$;


--
-- Name: trigger_set_created_by(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.trigger_set_created_by() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.created_by = current_user;
    RETURN NEW;
END;
$$;


--
-- Name: trigger_set_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.trigger_set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


--
-- Name: trigger_set_updated_by(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.trigger_set_updated_by() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_by = current_user;
    RETURN NEW;
END;
$$;


--
-- Name: validate_code_artifacts_cbor_auxdata(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_code_artifacts_cbor_auxdata(cbor_auxdata jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN is_jsonb_null(cbor_auxdata) OR (
        is_jsonb_object(cbor_auxdata) AND
        validate_code_artifacts_cbor_auxdata_internal(cbor_auxdata)
    );
END;
$$;


--
-- Name: validate_code_artifacts_cbor_auxdata_internal(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_code_artifacts_cbor_auxdata_internal(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    are_object_values_valid bool;
BEGIN
    SELECT bool_and (
        -- file name must be non-empty string
        length(key) > 0 AND
        -- the corresponding value is expected to be an object with only 'value' and 'offset' keys
        is_jsonb_object(value) AND
        validate_json_object_keys(value, array ['value', 'offset'], array []::text[]) AND
        -- the value of 'value' key is expected to be a non-empty hex string
        is_jsonb_string(value -> 'value') AND
        is_valid_hex(value ->> 'value', '+') AND
        -- the value of 'offset' key is expected to be a non-negative integer
        is_jsonb_number(value -> 'offset') AND
        (value->>'offset')::int >= 0
    )
    INTO are_object_values_valid
    FROM jsonb_each(obj);

    RETURN are_object_values_valid;
END;
$$;


--
-- Name: validate_code_artifacts_immutable_references(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_code_artifacts_immutable_references(immutable_references jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN is_jsonb_null(immutable_references) OR (
        is_jsonb_object(immutable_references) AND
        validate_code_artifacts_immutable_references_internal(immutable_references)
    );
END;
$$;


--
-- Name: validate_code_artifacts_immutable_references_internal(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_code_artifacts_immutable_references_internal(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    are_values_valid bool;
BEGIN
    SELECT bool_and (
        -- id must be non-empty string
        length(key) > 0 AND
        -- the corresponding value is expected to be an array of objects
        is_jsonb_array(value) AND (
            SELECT bool_and (
                is_jsonb_object(_references) AND
                -- expected only 'start' (non-negative number) and 'length' (positive number) key-values
                validate_json_object_keys(_references, array ['start', 'length'], array []::text[]) AND
                is_jsonb_number(_references->'start') AND
                (_references->'start')::int >= 0 AND
                is_jsonb_number(_references->'length') AND
                (_references->'length')::int > 0
            )
            FROM jsonb_array_elements(value) _references
        )
    )
    INTO are_values_valid
    FROM jsonb_each(obj);

    RETURN are_values_valid;
END;
$$;


--
-- Name: validate_code_artifacts_link_references(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_code_artifacts_link_references(link_references jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN is_jsonb_null(link_references) OR (
        is_jsonb_object(link_references) AND
        validate_code_artifacts_link_references_internal(link_references)
    );
END;
$$;


--
-- Name: validate_code_artifacts_link_references_internal(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_code_artifacts_link_references_internal(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    are_file_levels_valid bool;
BEGIN
    SELECT bool_and (
        -- file name must be non-empty string
        length(key) > 0 AND
        -- the corresponding value is expected to be an object with library names as keys
        is_jsonb_object(value) AND
        validate_code_artifacts_link_references_internal_file_libraries(value)
    )
    INTO are_file_levels_valid
    FROM jsonb_each(obj);

    RETURN are_file_levels_valid;
END;
$$;


--
-- Name: validate_code_artifacts_link_references_internal_file_libraries(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_code_artifacts_link_references_internal_file_libraries(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    are_file_libraries_valid bool;
BEGIN
    SELECT bool_and (
        -- library name must be non-empty string
        length(key) > 0 AND
        -- the corresponding value is expected to be an array of objects
        is_jsonb_array(value) AND (
            SELECT bool_and (
                is_jsonb_object(library_references) AND
                -- expected only 'start' (non-negative number) and 'length' (number always equals to 20) key-values
                validate_json_object_keys(library_references, array ['start', 'length'], array []::text[]) AND
                is_jsonb_number(library_references->'start') AND
                (library_references->'start')::int >= 0 AND
                is_jsonb_number(library_references->'length') AND
                (library_references->'length')::int = 20
            )
            FROM jsonb_array_elements(value) library_references
        )
    )
    INTO are_file_libraries_valid
    FROM jsonb_each(obj);

    RETURN are_file_libraries_valid;
END;
$$;


--
-- Name: validate_compilation_artifacts(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_compilation_artifacts(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
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
$$;


--
-- Name: validate_compilation_artifacts_abi(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_compilation_artifacts_abi(abi jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN is_jsonb_null(abi) OR is_jsonb_array(abi);
END;
$$;


--
-- Name: validate_compilation_artifacts_sources(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_compilation_artifacts_sources(sources jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN is_jsonb_null(sources) OR (
        is_jsonb_object(sources) AND
        validate_compilation_artifacts_sources_internal(sources)
    );
END;
$$;


--
-- Name: validate_compilation_artifacts_sources_internal(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_compilation_artifacts_sources_internal(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    are_object_values_valid bool;
    are_ids_unique          bool;
BEGIN
    SELECT bool_and (
        -- file name must be non-empty string
       length(key) > 0 AND
       -- the corresponding value is expected to be an object with only the 'id' key
       is_jsonb_object(value) AND
       validate_json_object_keys(value, array ['id'], array []::text[]) AND
       -- the value of 'id' key is expected to be a non-negative integer
       is_jsonb_number(value -> 'id') AND
       (value->>'id')::int >= 0
    )
    INTO are_object_values_valid
    FROM jsonb_each(obj);

    SELECT count(value -> 'id') = count(DISTINCT value -> 'id')
    INTO are_ids_unique
    FROM jsonb_each(obj);

    RETURN are_object_values_valid AND are_ids_unique;
END;
$$;


--
-- Name: validate_creation_code_artifacts(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_creation_code_artifacts(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        is_jsonb_object(obj) AND
        validate_json_object_keys(
            obj,
            array ['sourceMap', 'linkReferences'],
            array ['cborAuxdata']
        ) AND
        validate_code_artifacts_cbor_auxdata(coalesce(obj -> 'cborAuxdata', 'null'::jsonb)) AND
        validate_code_artifacts_link_references(obj -> 'linkReferences');
END;
$$;


--
-- Name: validate_creation_transformations(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_creation_transformations(transformations jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        is_jsonb_array(transformations) AND
        validate_transformations(transformations, array ['constructorArguments', 'library', 'cborAuxdata']);
END;
$$;


--
-- Name: validate_creation_values(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_creation_values(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        is_jsonb_object(obj) AND
        validate_json_object_keys(
            obj,
            array []::text[],
            array ['constructorArguments', 'libraries', 'cborAuxdata']
        ) AND
        validate_values_constructor_arguments(obj) AND
        validate_values_libraries(obj) AND
        validate_values_cbor_auxdata(obj);
END;
$$;


--
-- Name: validate_json_object_keys(jsonb, text[], text[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_json_object_keys(obj jsonb, mandatory_keys text[], optional_keys text[]) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        -- ensures that all keys on the right exist as keys inside obj
        obj ?& mandatory_keys AND
        -- check that no unknown key exists inside obj
        bool_and(obj_keys = any (mandatory_keys || optional_keys))
        from (select obj_keys from jsonb_object_keys(obj) as obj_keys) as subquery;
END;
$$;


--
-- Name: validate_runtime_code_artifacts(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_runtime_code_artifacts(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        is_jsonb_object(obj) AND
        validate_json_object_keys(
            obj,
            array ['sourceMap', 'linkReferences', 'immutableReferences'],
            array ['cborAuxdata']
        ) AND
        validate_code_artifacts_cbor_auxdata(coalesce(obj -> 'cborAuxdata', 'null'::jsonb)) AND
        validate_code_artifacts_link_references(obj -> 'linkReferences') AND
        validate_code_artifacts_immutable_references(obj -> 'immutableReferences');
END;
$$;


--
-- Name: validate_runtime_transformations(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_runtime_transformations(transformations jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        is_jsonb_array(transformations) AND
        validate_transformations(transformations, array ['library', 'immutable', 'cborAuxdata', 'callProtection']);
END;
$$;


--
-- Name: validate_runtime_values(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_runtime_values(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN
        is_jsonb_object(obj) AND
        validate_json_object_keys(
            obj,
            array []::text[],
            array ['libraries', 'immutables', 'cborAuxdata', 'callProtection']
        ) AND
        validate_values_libraries(obj) AND
        validate_values_immutables(obj) AND
        validate_values_cbor_auxdata(obj) AND
        validate_values_call_protection(obj);
END;
$$;


--
-- Name: validate_transformation_key_id(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformation_key_id(object jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN object ? 'id' AND is_jsonb_string(object -> 'id') AND length(object ->> 'id') > 0;
END;
$$;


--
-- Name: validate_transformation_key_offset(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformation_key_offset(object jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN object ? 'offset' AND is_jsonb_number(object -> 'offset') AND (object ->> 'offset')::integer >= 0;
END;
$$;


--
-- Name: validate_transformation_key_type(jsonb, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformation_key_type(object jsonb, expected_value text) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN object ? 'type' AND is_jsonb_string(object -> 'type') AND object ->> 'type' = expected_value;
END;
$$;


--
-- Name: validate_transformations(jsonb, text[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformations(transformations jsonb, allowed_reasons text[]) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    transformation_object jsonb;
    reason                text;
BEGIN
    FOR transformation_object IN SELECT * FROM jsonb_array_elements(transformations)
        LOOP
            IF NOT is_jsonb_object(transformation_object)
                OR NOT transformation_object ? 'reason'
                OR NOT is_jsonb_string(transformation_object -> 'reason')
                OR array_position(allowed_reasons, transformation_object ->> 'reason') IS NULL
            THEN
                RETURN false;
            END IF;

            reason := transformation_object ->> 'reason';

            CASE
                WHEN reason = 'constructorArguments'
                    THEN RETURN validate_transformations_constructor_arguments(transformation_object);
                WHEN reason = 'library' THEN RETURN validate_transformations_library(transformation_object);
                WHEN reason = 'immutable' THEN RETURN validate_transformations_immutable(transformation_object);
                WHEN reason = 'cborAuxdata' THEN RETURN validate_transformations_cbor_auxdata(transformation_object);
                WHEN reason = 'callProtection'
                    THEN RETURN validate_transformations_call_protection(transformation_object);
                ELSE
                END CASE;

        END LOOP;

    RETURN true;
END;
$$;


--
-- Name: validate_transformations_call_protection(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformations_call_protection(object jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN validate_transformation_key_type(object, 'replace')
        -- 'callProtection' value is always located at offset 1
        AND validate_transformation_key_offset(object) AND (object ->> 'offset')::integer = 1;
END;
$$;


--
-- Name: validate_transformations_cbor_auxdata(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformations_cbor_auxdata(object jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN validate_transformation_key_type(object, 'replace') AND validate_transformation_key_offset(object)
        AND validate_transformation_key_id(object);
END;
$$;


--
-- Name: validate_transformations_constructor_arguments(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformations_constructor_arguments(object jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN validate_transformation_key_type(object, 'insert') AND validate_transformation_key_offset(object);
END;
$$;


--
-- Name: validate_transformations_immutable(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformations_immutable(object jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN (validate_transformation_key_type(object, 'replace') OR validate_transformation_key_type(object, 'insert')) AND validate_transformation_key_offset(object)
        AND validate_transformation_key_id(object);
END;
$$;


--
-- Name: validate_transformations_library(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_transformations_library(object jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN validate_transformation_key_type(object, 'replace') AND validate_transformation_key_offset(object)
        AND validate_transformation_key_id(object);
END;
$$;


--
-- Name: validate_values_call_protection(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_values_call_protection(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- `obj` does not contain 'callProtection' key
    IF NOT obj ? 'callProtection' THEN
        RETURN true;
    END IF;

    RETURN is_jsonb_string(obj -> 'callProtection')
               AND is_valid_hex(obj ->> 'callProtection', '{20}');
END;
$$;


--
-- Name: validate_values_cbor_auxdata(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_values_cbor_auxdata(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- `obj` does not contain 'cborAuxdata' key
    IF NOT obj ? 'cborAuxdata' THEN
        RETURN true;
    END IF;

    IF NOT is_jsonb_object(obj -> 'cborAuxdata') THEN
        RETURN false;
    END IF;

    RETURN bool_and(
        length(key) > 0 AND
        is_jsonb_string(value) AND
        is_valid_hex(value ->> 0, '+')
    )
    FROM jsonb_each(obj -> 'cborAuxdata');
END;
$$;


--
-- Name: validate_values_constructor_arguments(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_values_constructor_arguments(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- `obj` does not contain 'constructorArguments' key
    IF NOT obj ? 'constructorArguments' THEN
        RETURN true;
    END IF;

    RETURN is_jsonb_string(obj -> 'constructorArguments')
               AND is_valid_hex(obj ->> 'constructorArguments', '+');
END;
$$;


--
-- Name: validate_values_immutables(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_values_immutables(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- `obj` does not contain 'immutables' key
    IF NOT obj ? 'immutables' THEN
        RETURN true;
    END IF;

    IF NOT is_jsonb_object(obj -> 'immutables') THEN
        RETURN false;
    END IF;

    RETURN bool_and(
        length(key) > 0 AND
        is_jsonb_string(value) AND
        is_valid_hex(value ->> 0, '+')
    )
    FROM jsonb_each(obj -> 'immutables');
END;
$$;


--
-- Name: validate_values_libraries(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_values_libraries(obj jsonb) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- `obj` does not contain 'libraries' key
    IF NOT obj ? 'libraries' THEN
        RETURN true;
    END IF;

    IF NOT is_jsonb_object(obj -> 'libraries') THEN
        RETURN false;
    END IF;

    RETURN bool_and(
        length(key) > 0 AND
        is_jsonb_string(value) AND
        is_valid_hex(value ->> 0, '{20}')
    )
    FROM jsonb_each(obj -> 'libraries');
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: code; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.code (
    code_hash bytea NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying DEFAULT CURRENT_USER NOT NULL,
    updated_by character varying DEFAULT CURRENT_USER NOT NULL,
    code_hash_keccak bytea NOT NULL,
    code bytea,
    CONSTRAINT code_hash_check CHECK ((((code IS NOT NULL) AND (code_hash = public.digest(code, 'sha256'::text))) OR ((code IS NULL) AND (code_hash = '\x'::bytea))))
);


--
-- Name: compiled_contracts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.compiled_contracts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying DEFAULT CURRENT_USER NOT NULL,
    updated_by character varying DEFAULT CURRENT_USER NOT NULL,
    compiler character varying NOT NULL,
    version character varying NOT NULL,
    language character varying NOT NULL,
    name character varying NOT NULL,
    fully_qualified_name character varying NOT NULL,
    compiler_settings jsonb NOT NULL,
    compilation_artifacts jsonb NOT NULL,
    creation_code_hash bytea NOT NULL,
    creation_code_artifacts jsonb NOT NULL,
    runtime_code_hash bytea NOT NULL,
    runtime_code_artifacts jsonb NOT NULL,
    CONSTRAINT compilation_artifacts_json_schema CHECK (public.validate_compilation_artifacts(compilation_artifacts)),
    CONSTRAINT creation_code_artifacts_json_schema CHECK (public.validate_creation_code_artifacts(creation_code_artifacts)),
    CONSTRAINT runtime_code_artifacts_json_schema CHECK (public.validate_runtime_code_artifacts(runtime_code_artifacts))
);


--
-- Name: compiled_contracts_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.compiled_contracts_sources (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    compilation_id uuid NOT NULL,
    source_hash bytea NOT NULL,
    path character varying NOT NULL
);


--
-- Name: contract_deployments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contract_deployments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying DEFAULT CURRENT_USER NOT NULL,
    updated_by character varying DEFAULT CURRENT_USER NOT NULL,
    chain_id bigint NOT NULL,
    address bytea NOT NULL,
    transaction_hash bytea NOT NULL,
    block_number numeric NOT NULL,
    transaction_index numeric NOT NULL,
    deployer bytea NOT NULL,
    contract_id uuid NOT NULL
);


--
-- Name: contracts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contracts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying DEFAULT CURRENT_USER NOT NULL,
    updated_by character varying DEFAULT CURRENT_USER NOT NULL,
    creation_code_hash bytea NOT NULL,
    runtime_code_hash bytea NOT NULL
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


--
-- Name: sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sources (
    source_hash bytea NOT NULL,
    source_hash_keccak bytea NOT NULL,
    content character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying DEFAULT CURRENT_USER NOT NULL,
    updated_by character varying DEFAULT CURRENT_USER NOT NULL,
    CONSTRAINT source_hash_check CHECK ((source_hash = public.digest((content)::text, 'sha256'::text)))
);


--
-- Name: verified_contracts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.verified_contracts (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying DEFAULT CURRENT_USER NOT NULL,
    updated_by character varying DEFAULT CURRENT_USER NOT NULL,
    deployment_id uuid NOT NULL,
    compilation_id uuid NOT NULL,
    creation_match boolean NOT NULL,
    creation_values jsonb,
    creation_transformations jsonb,
    creation_metadata_match boolean,
    runtime_match boolean NOT NULL,
    runtime_values jsonb,
    runtime_transformations jsonb,
    runtime_metadata_match boolean,
    CONSTRAINT creation_transformations_json_schema CHECK (((creation_transformations IS NULL) OR public.validate_creation_transformations(creation_transformations))),
    CONSTRAINT creation_values_json_schema CHECK (((creation_values IS NULL) OR public.validate_creation_values(creation_values))),
    CONSTRAINT runtime_transformations_json_schema CHECK (((runtime_transformations IS NULL) OR public.validate_runtime_transformations(runtime_transformations))),
    CONSTRAINT runtime_values_json_schema CHECK (((runtime_values IS NULL) OR public.validate_runtime_values(runtime_values))),
    CONSTRAINT verified_contracts_creation_match_integrity CHECK ((((creation_match = false) AND (creation_values IS NULL) AND (creation_transformations IS NULL) AND (creation_metadata_match IS NULL)) OR ((creation_match = true) AND (creation_values IS NOT NULL) AND (creation_transformations IS NOT NULL) AND (creation_metadata_match IS NOT NULL)))),
    CONSTRAINT verified_contracts_match_exists CHECK (((creation_match = true) OR (runtime_match = true))),
    CONSTRAINT verified_contracts_runtime_match_integrity CHECK ((((runtime_match = false) AND (runtime_values IS NULL) AND (runtime_transformations IS NULL) AND (runtime_metadata_match IS NULL)) OR ((runtime_match = true) AND (runtime_values IS NOT NULL) AND (runtime_transformations IS NOT NULL) AND (runtime_metadata_match IS NOT NULL))))
);


--
-- Name: verified_contracts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.verified_contracts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: verified_contracts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.verified_contracts_id_seq OWNED BY public.verified_contracts.id;


--
-- Name: verified_contracts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verified_contracts ALTER COLUMN id SET DEFAULT nextval('public.verified_contracts_id_seq'::regclass);


--
-- Name: code code_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.code
    ADD CONSTRAINT code_pkey PRIMARY KEY (code_hash);


--
-- Name: compiled_contracts compiled_contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts
    ADD CONSTRAINT compiled_contracts_pkey PRIMARY KEY (id);


--
-- Name: compiled_contracts compiled_contracts_pseudo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts
    ADD CONSTRAINT compiled_contracts_pseudo_pkey UNIQUE (compiler, language, creation_code_hash, runtime_code_hash);


--
-- Name: compiled_contracts_sources compiled_contracts_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts_sources
    ADD CONSTRAINT compiled_contracts_sources_pkey PRIMARY KEY (id);


--
-- Name: compiled_contracts_sources compiled_contracts_sources_pseudo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts_sources
    ADD CONSTRAINT compiled_contracts_sources_pseudo_pkey UNIQUE (compilation_id, path);


--
-- Name: contract_deployments contract_deployments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contract_deployments
    ADD CONSTRAINT contract_deployments_pkey PRIMARY KEY (id);


--
-- Name: contract_deployments contract_deployments_pseudo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contract_deployments
    ADD CONSTRAINT contract_deployments_pseudo_pkey UNIQUE (chain_id, address, transaction_hash);


--
-- Name: contracts contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pkey PRIMARY KEY (id);


--
-- Name: contracts contracts_pseudo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pseudo_pkey UNIQUE (creation_code_hash, runtime_code_hash);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: sources sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (source_hash);


--
-- Name: verified_contracts verified_contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verified_contracts
    ADD CONSTRAINT verified_contracts_pkey PRIMARY KEY (id);


--
-- Name: verified_contracts verified_contracts_pseudo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verified_contracts
    ADD CONSTRAINT verified_contracts_pseudo_pkey UNIQUE (compilation_id, deployment_id);


--
-- Name: code_code_hash_keccak; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX code_code_hash_keccak ON public.code USING btree (code_hash_keccak);


--
-- Name: compiled_contracts_creation_code_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX compiled_contracts_creation_code_hash ON public.compiled_contracts USING btree (creation_code_hash);


--
-- Name: compiled_contracts_runtime_code_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX compiled_contracts_runtime_code_hash ON public.compiled_contracts USING btree (runtime_code_hash);


--
-- Name: compiled_contracts_sources_compilation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX compiled_contracts_sources_compilation_id ON public.compiled_contracts_sources USING btree (compilation_id);


--
-- Name: compiled_contracts_sources_source_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX compiled_contracts_sources_source_hash ON public.compiled_contracts_sources USING btree (source_hash);


--
-- Name: contract_deployments_address; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contract_deployments_address ON public.contract_deployments USING btree (address);


--
-- Name: contract_deployments_contract_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contract_deployments_contract_id ON public.contract_deployments USING btree (contract_id);


--
-- Name: contracts_creation_code_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contracts_creation_code_hash ON public.contracts USING btree (creation_code_hash);


--
-- Name: contracts_creation_code_hash_runtime_code_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contracts_creation_code_hash_runtime_code_hash ON public.contracts USING btree (creation_code_hash, runtime_code_hash);


--
-- Name: contracts_runtime_code_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contracts_runtime_code_hash ON public.contracts USING btree (runtime_code_hash);


--
-- Name: verified_contracts_compilation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX verified_contracts_compilation_id ON public.verified_contracts USING btree (compilation_id);


--
-- Name: verified_contracts_deployment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX verified_contracts_deployment_id ON public.verified_contracts USING btree (deployment_id);


--
-- Name: code insert_set_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_at BEFORE INSERT ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_at();


--
-- Name: compiled_contracts insert_set_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_at BEFORE INSERT ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_at();


--
-- Name: contract_deployments insert_set_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_at BEFORE INSERT ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_at();


--
-- Name: contracts insert_set_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_at BEFORE INSERT ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_at();


--
-- Name: sources insert_set_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_at BEFORE INSERT ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_at();


--
-- Name: verified_contracts insert_set_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_at BEFORE INSERT ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_at();


--
-- Name: code insert_set_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_by BEFORE INSERT ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_by();


--
-- Name: compiled_contracts insert_set_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_by BEFORE INSERT ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_by();


--
-- Name: contract_deployments insert_set_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_by BEFORE INSERT ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_by();


--
-- Name: contracts insert_set_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_by BEFORE INSERT ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_by();


--
-- Name: sources insert_set_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_by BEFORE INSERT ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_by();


--
-- Name: verified_contracts insert_set_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_created_by BEFORE INSERT ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_created_by();


--
-- Name: code insert_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_at BEFORE INSERT ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: compiled_contracts insert_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_at BEFORE INSERT ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: contract_deployments insert_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_at BEFORE INSERT ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: contracts insert_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_at BEFORE INSERT ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: sources insert_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_at BEFORE INSERT ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: verified_contracts insert_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_at BEFORE INSERT ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: code insert_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_by BEFORE INSERT ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: compiled_contracts insert_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_by BEFORE INSERT ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: contract_deployments insert_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_by BEFORE INSERT ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: contracts insert_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_by BEFORE INSERT ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: sources insert_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_by BEFORE INSERT ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: verified_contracts insert_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER insert_set_updated_by BEFORE INSERT ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: code update_reuse_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_at BEFORE UPDATE ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_at();


--
-- Name: compiled_contracts update_reuse_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_at BEFORE UPDATE ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_at();


--
-- Name: contract_deployments update_reuse_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_at BEFORE UPDATE ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_at();


--
-- Name: contracts update_reuse_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_at BEFORE UPDATE ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_at();


--
-- Name: sources update_reuse_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_at BEFORE UPDATE ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_at();


--
-- Name: verified_contracts update_reuse_created_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_at BEFORE UPDATE ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_at();


--
-- Name: code update_reuse_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_by BEFORE UPDATE ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_by();


--
-- Name: compiled_contracts update_reuse_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_by BEFORE UPDATE ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_by();


--
-- Name: contract_deployments update_reuse_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_by BEFORE UPDATE ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_by();


--
-- Name: contracts update_reuse_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_by BEFORE UPDATE ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_by();


--
-- Name: sources update_reuse_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_by BEFORE UPDATE ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_by();


--
-- Name: verified_contracts update_reuse_created_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_reuse_created_by BEFORE UPDATE ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_reuse_created_by();


--
-- Name: code update_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_at BEFORE UPDATE ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: compiled_contracts update_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_at BEFORE UPDATE ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: contract_deployments update_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_at BEFORE UPDATE ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: contracts update_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_at BEFORE UPDATE ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: sources update_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_at BEFORE UPDATE ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: verified_contracts update_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_at BEFORE UPDATE ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();


--
-- Name: code update_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_by BEFORE UPDATE ON public.code FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: compiled_contracts update_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_by BEFORE UPDATE ON public.compiled_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: contract_deployments update_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_by BEFORE UPDATE ON public.contract_deployments FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: contracts update_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_by BEFORE UPDATE ON public.contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: sources update_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_by BEFORE UPDATE ON public.sources FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: verified_contracts update_set_updated_by; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_set_updated_by BEFORE UPDATE ON public.verified_contracts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_by();


--
-- Name: compiled_contracts compiled_contracts_creation_code_hash_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts
    ADD CONSTRAINT compiled_contracts_creation_code_hash_fkey FOREIGN KEY (creation_code_hash) REFERENCES public.code(code_hash);


--
-- Name: compiled_contracts compiled_contracts_runtime_code_hash_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts
    ADD CONSTRAINT compiled_contracts_runtime_code_hash_fkey FOREIGN KEY (runtime_code_hash) REFERENCES public.code(code_hash);


--
-- Name: compiled_contracts_sources compiled_contracts_sources_compilation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts_sources
    ADD CONSTRAINT compiled_contracts_sources_compilation_id_fkey FOREIGN KEY (compilation_id) REFERENCES public.compiled_contracts(id);


--
-- Name: compiled_contracts_sources compiled_contracts_sources_source_hash_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compiled_contracts_sources
    ADD CONSTRAINT compiled_contracts_sources_source_hash_fkey FOREIGN KEY (source_hash) REFERENCES public.sources(source_hash);


--
-- Name: contract_deployments contract_deployments_contract_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contract_deployments
    ADD CONSTRAINT contract_deployments_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES public.contracts(id);


--
-- Name: contracts contracts_creation_code_hash_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_creation_code_hash_fkey FOREIGN KEY (creation_code_hash) REFERENCES public.code(code_hash);


--
-- Name: contracts contracts_runtime_code_hash_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_runtime_code_hash_fkey FOREIGN KEY (runtime_code_hash) REFERENCES public.code(code_hash);


--
-- Name: verified_contracts verified_contracts_compilation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verified_contracts
    ADD CONSTRAINT verified_contracts_compilation_id_fkey FOREIGN KEY (compilation_id) REFERENCES public.compiled_contracts(id);


--
-- Name: verified_contracts verified_contracts_deployment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verified_contracts
    ADD CONSTRAINT verified_contracts_deployment_id_fkey FOREIGN KEY (deployment_id) REFERENCES public.contract_deployments(id);


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20250717103432'),
    ('20250723145429');
