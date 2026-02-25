from helpers import *


@pytest.fixture(scope='function', autouse=True)
def setup(connection, dummy_code):
    dummy_code.insert(connection)


class TestAdditionalInput:
    def test_null_succeeds(self, connection, dummy_code, dummy_compiled_contract):
        # additional_input defaults to SQL NULL when not set
        dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash)

    def test_storage_layout_overrides_succeeds(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.additional_input = {
            "storage_layout_overrides": {
                "x": {"slot": "0x0", "type": "uint256", "n_slots": 1}
            }
        }
        dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash)

    def test_empty_object_succeeds(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.additional_input = {}
        dummy_compiled_contract.insert(connection, dummy_code.code_hash, dummy_code.code_hash)

    def test_unknown_key_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.additional_input = {"unknown_key": {}}
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'additional_input_json_schema')

    def test_unknown_key_alongside_valid_key_fails(self, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.additional_input = {
            "storage_layout_overrides": {},
            "unknown_key": {}
        }
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'additional_input_json_schema')

    @pytest.mark.parametrize("value", ["a string", [1, 2], 42], ids=["string", "array", "number"])
    def test_non_object_type_fails(self, value, connection, dummy_code, dummy_compiled_contract):
        dummy_compiled_contract.additional_input = value
        check_constraint_fails(
            lambda: dummy_compiled_contract.insert(
                connection, dummy_code.code_hash, dummy_code.code_hash),
            'additional_input_json_schema')
