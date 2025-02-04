from helpers import *


@pytest.fixture(scope='function', autouse=True)
def setup(connection, dummy_code):
    dummy_code.insert(connection)


class TestObject:
    # All required fields as null objects ('cborAuxdata' is not required)
    def test_required_fields_as_nones(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts = dict({
            "sourceMap": None,
            "linkReferences": None,
            "immutableReferences": None,
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    # 'cborAuxdata' is optional
    def test_with_cbor_auxdata(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts = dict({
            "sourceMap": None,
            "linkReferences": None,
            "immutableReferences": None,
            "cborAuxdata": None,
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    # Fields with expected type values
    def test_expected_type_values(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts = dict({
            "sourceMap": "",
            "linkReferences": {},
            "immutableReferences": {},
            "cborAuxdata": {}
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    # Field types are not strictly defined and may be any valid json values
    def test_valid_object_with_random_json_values(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts = dict({
            "sourceMap": [],
            "linkReferences": None,
            "immutableReferences": [""],
            "cborAuxdata": None
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    def test_type_none_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts = None
        check_constraint_fails(lambda: dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash), 'runtime_code_artifacts_json_schema')

    def test_invalid_json_type_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts = "just a string"
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'runtime_code_artifacts_json_schema')

    def test_missing_source_map_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts.pop("sourceMap")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'runtime_code_artifacts_json_schema')

    def test_missing_link_references_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts.pop("linkReferences")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'runtime_code_artifacts_json_schema')


########## Tests cbor_auxdata field constraints ##########
class TestCborAuxdata:
    def test_valid_field_value(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"value": "0x1234", "offset": 0}}
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    @pytest.mark.parametrize("value", [0, "", []], ids=["number", "string", "array"])
    def test_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = value
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_id_is_empty_string_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "": {"value": "0x1234", "offset": 0}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [None, 0, "", []], ids=["null", "number", "string", "array"])
    def test_id_value_has_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": value}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_value_subkey_is_missing_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"offset": 0}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_offset_subkey_is_missing_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"value": "0x1234"}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_unknown_subkey_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"value": "0x1234", "offset": 0, "unknown": None}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [None, 0, [], {}], ids=["null", "number", "array", "object"])
    def test_value_subkey_has_invalid_type_fails(self, value, connection, dummy_code,
                                                 dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"value": value, "offset": 0}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", ["1234", "0xqw1234", "0x123", "0x"], ids=["without_0x_prefix", "not_valid_hex", "odd_number_of_symbols", "zero_length"])
    def test_value_subkey_has_invalid_value_fails(self, value, connection, dummy_code,
                                                  dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"value": value, "offset": 0}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [None, "", [], {}], ids=["null", "string", "array", "object"])
    def test_offset_subkey_has_invalid_type_fails(self, value, connection, dummy_code,
                                                  dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"value": "0x1234", "offset": value}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [-1], ids=["negative"])
    def test_offset_subkey_has_invalid_value_fails(self, value, connection, dummy_code,
                                                   dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id": {"value": "0x1234", "offset": value}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_that_all_ids_are_checked(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['cborAuxdata'] = {
            "id1": {"value": "0x1234", "offset": 0}, "id2": {"value": "0x1234", "offset": -1}
        }
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema'
        )


class TestLinkReferences:
    def test_valid_field_value(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": 0, "length": 20}]}}
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    @pytest.mark.parametrize("value", [0, "", []], ids=["number", "string", "array"])
    def test_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = value
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_file_name_is_empty_string_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": 0, "length": 20}]}, "": {"library": [{"start": 0, "length": 20}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [None, 0, "", []], ids=["null", "number", "string", "array"])
    def test_file_name_value_has_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": value}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_library_name_is_empty_string_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"": [{"start": 0, "length": 20}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [None, 0, "", dict()], ids=["null", "number", "string", "object"])
    def test_library_name_value_has_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": value}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_unknown_subkey_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": 0, "length": 20, "unknown": None}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_start_subkey_is_missing_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"length": 20}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [None, "", [], dict()], ids=["null", "string", "array", "object"])
    def test_start_subkey_has_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": value, "length": 20}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [-1], ids=["negative"])
    def test_start_subkey_has_invalid_value_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": value, "length": 20}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    def test_length_subkey_is_missing_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": 0}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [None, "", [], dict()], ids=["null", "string", "array", "object"])
    def test_length_subkey_has_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": 0, "length": value}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    @pytest.mark.parametrize("value", [-1, 0, 22], ids=["negative", "zero", "positive_not_20"])
    def test_length_subkey_has_invalid_value_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library": [{"start": 0, "length": value}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    # tries to validate that if several file names exist, all of them are validated
    def test_that_all_file_names_are_checked(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name1.sol": {"library": [{"start": 0, "length": 20}]},
            "file_name2.sol": {"": [{"start": 0, "length": 20}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    # tries to validate that if several libraries exist per file, all of them are validated
    def test_that_all_file_libraries_are_checked(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library1": [{"start": 0, "length": 20}], "library2": [{"start": 0, "length": 0}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')

    # tries to validate that if several references exist per library, all of them are validated
    def test_that_all_library_references_are_checked(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.runtime_code_artifacts['linkReferences'] = {
            "file_name.sol": {"library1": [{"start": 0, "length": 20}, {"start": 100, "length": 0}]}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'runtime_code_artifacts_json_schema')
