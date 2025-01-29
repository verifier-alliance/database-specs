from helpers import *


@pytest.fixture(scope='function', autouse=True)
def setup(connection, dummy_code):
    dummy_code.insert(connection)


class TestObject:
    # All required fields as null objects
    def test_required_fields_as_nones(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts = dict({
            "abi": None,
            "userdoc": None,
            "devdoc": None,
            "sources": None,
            "storageLayout": None
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    # Fields with expected type values
    def test_expected_type_values(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts = dict({
            "abi": [],
            "userdoc": {},
            "devdoc": {},
            "sources": {},
            "storageLayout": {}
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    # Field types are not strictly defined and may be any valid json values
    def test_random_json_values(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts = dict({
            "abi": "",
            "userdoc": [""],
            "devdoc": {"devdoc": ["value"]},
            "sources": {"file.sol": {"id": 0}},
            "storageLayout": None
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    def test_type_none_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts = None
        check_constraint_fails(lambda: dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    def test_invalid_json_type_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts = "just a string"
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    def test_missing_abi_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("abi")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    def test_missing_userdoc_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("userdoc")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    def test_missing_devdoc_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("devdoc")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    def test_missing_sources_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("sources")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    def test_missing_storage_layout_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("storageLayout")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    def test_unknown_field_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['unknown_key'] = None
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_json_schema')

    @pytest.mark.parametrize("value", [0, "", []], ids=["number", "string", "array"])
    def test_sources_invalid_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = value
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), "compilation_artifacts_json_schema")

    def test_sources_file_name_empty_string_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = {
            "file.sol": {"id": 0}, "": {"id": 1}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            "compilation_artifacts_json_schema")

    @pytest.mark.parametrize("value", [None, 0, "", []], ids=["null", "number", "string", "array"])
    def test_sources_id_subkey_values_invalid_type_fails(self, value, connection, dummy_code,
                                                         dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = {
            "file.sol": value}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            "compilation_artifacts_json_schema")

    def test_sources_missing_id_subkey_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = {
            "file.sol": {}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            "compilation_artifacts_json_schema")

    def test_sources_extra_subkey_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = {
            "file.sol": {"id": 0, "extra": 1}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            "compilation_artifacts_json_schema")

    @pytest.mark.parametrize("value", [None, "", [], dict()], ids=["null", "string", "array", "object"])
    def test_sources_id_subkey_value_type_is_not_number_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = {
            "file.sol": {"id": value}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            "compilation_artifacts_json_schema")

    def test_sources_id_subkey_value_is_negative_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = {
            "file.sol": {"id": -1}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash
            ), "compilation_artifacts_json_schema"
        )

    def test_sources_repetitive_id_subkey_values_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['sources'] = {
            "file.sol": {"id": 0}, "file2.sol": {"id": 0}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            "compilation_artifacts_json_schema")
