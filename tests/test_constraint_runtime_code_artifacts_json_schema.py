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
            "linkReferences": "",
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
