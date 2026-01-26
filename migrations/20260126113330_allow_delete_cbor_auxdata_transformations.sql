-- migrate:up
CREATE OR REPLACE FUNCTION validate_transformations_cbor_auxdata(object jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN (
            validate_transformation_key_type(object, 'replace')
            OR validate_transformation_key_type(object, 'delete')
        ) AND validate_transformation_key_offset(object);
END;
$$ LANGUAGE plpgsql;

-- migrate:down
CREATE OR REPLACE FUNCTION validate_transformations_cbor_auxdata(object jsonb)
    RETURNS boolean AS
$$
BEGIN
    RETURN validate_transformation_key_type(object, 'replace') AND validate_transformation_key_offset(object)
        AND validate_transformation_key_id(object);
END;
$$ LANGUAGE plpgsql;
