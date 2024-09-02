from helpers import *


class TestCompilationArtifactsConstraints:
    @pytest.fixture(scope='function', autouse=True)
    def insert_dummy_code(self, connection, dummy_code):
        dummy_code.insert(connection)

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
            "sources": [],
            "storageLayout": None
        })
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

    def test_type_none_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts = None
        check_constraint_fails(lambda: dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')

    def test_invalid_json_type_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts = "just a string"
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')

    def test_missing_abi_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("abi")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')

    def test_missing_userdoc_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("userdoc")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')

    def test_missing_devdoc_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("devdoc")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')

    def test_missing_sources_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("sources")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')

    def test_missing_storage_layout_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts.pop("storageLayout")
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')

    def test_unknown_field_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.compilation_artifacts['unknown_key'] = None
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash), 'compilation_artifacts_object')