-- migrate:up
CREATE OR REPLACE FUNCTION validate_transformation_key_length(object jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN object ? 'length' AND is_jsonb_number(object -> 'length') AND (object ->> 'length')::integer >= 0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validate_transformations_cbor_auxdata(object jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN (
        validate_transformation_key_type(object, 'replace')
        AND validate_transformation_key_offset(object)
        AND validate_transformation_key_id(object)
    ) OR (
        validate_transformation_key_type(object, 'delete')
        AND validate_transformation_key_offset(object)
        AND validate_transformation_key_length(object)
    );
END;
$$ LANGUAGE plpgsql;

-- migrate:down
DROP FUNCTION IF EXISTS validate_transformation_key_length(jsonb);

CREATE OR REPLACE FUNCTION validate_transformations_cbor_auxdata(object jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN validate_transformation_key_type(object, 'replace') AND validate_transformation_key_offset(object)
        AND validate_transformation_key_id(object);
END;
$$ LANGUAGE plpgsql;
