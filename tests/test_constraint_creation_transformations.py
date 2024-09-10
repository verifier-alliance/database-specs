from helpers import *


@pytest.fixture(scope='function', autouse=True)
def setup(connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
    dummy_code.insert(connection)
    dummy_contract.insert(
        connection, dummy_code.code_hash, dummy_code.code_hash)
    dummy_contract_deployment.insert(connection, dummy_contract.id)
    dummy_compiled_contract.insert(
        connection, dummy_code.code_hash, dummy_code.code_hash)


class TestCommon:
    def test_empty_array_is_allowed(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = []
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_expected_type_values(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "type": "insert", "offset": 0},
            {"reason": "library", "type": "replace",
                "offset": 0, "id": "file1:lib1"},
            {"reason": "cborAuxdata", "type": "replace", "offset": 0, "id": "0"}
        ]
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    @pytest.mark.parametrize("value", [None, "", dict()], ids=["null", "string", "object"])
    def test_invalid_json_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = value
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, "", []], ids=["null", "string", "array"])
    def test_invalid_transformation_value_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                                     dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [value]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_missing_key_reason_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"type": "insert", "offset": 0, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, [], dict()], ids=["null", "array", "object"])
    def test_invalid_key_reason_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": value, "type": "insert", "offset": 0, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_reason_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "unknownReason", "type": "insert", "offset": 0, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_immutable_reason_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "immutable", "type": "replace", "offset": 0, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_call_protection_reason_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "callProtection", "type": "replace", "offset": 1}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")


class TestConstructorArguments:
    def test_valid_value(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "type": "insert", "offset": 0}
        ]
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_missing_key_type_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "offset": 0}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, 0, [], dict()], ids=["null", "number", "array", "object"])
    def test_invalid_key_type_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "type": value, "offset": 0}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_type_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "type": "replace", "offset": 0}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_missing_key_offset_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "type": "insert"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, "", [], dict()], ids=["null", "string", "array", "object"])
    def test_invalid_key_offset_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "type": "insert", "offset": value}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_offset_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                            dummy_compiled_contract, dummy_verified_contract):
        # The offset must be >= 0
        dummy_verified_contract.creation_transformations = [
            {"reason": "constructorArguments", "type": "insert", "offset": -1}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")


class TestLibrary:
    def test_valid_value(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "replace",
                "offset": 0, "id": "file1:lib1"}
        ]
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_missing_key_type_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "offset": 0, "id": "file1:lib1"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, 0, [], dict()], ids=["null", "number", "array", "object"])
    def test_invalid_key_type_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": value, "offset": 0, "id": "file1:lib1"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_type_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "insert",
                "offset": 0, "id": "file1:lib1"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_missing_key_offset_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "replace", "id": "file1:lib1"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, "", [], dict()], ids=["null", "string", "array", "object"])
    def test_invalid_key_offset_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "replace",
                "offset": value, "id": "file1:lib1"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_offset_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                            dummy_compiled_contract, dummy_verified_contract):
        # The offset must be >= 0
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "replace",
                "offset": -1, "id": "file1:lib1"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_missing_key_id_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "replace", "offset": 0}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, 0, [], dict()], ids=["null", "number", "array", "object"])
    def test_invalid_key_id_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "replace", "offset": 0, "id": value}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_id_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                        dummy_compiled_contract, dummy_verified_contract):
        # The length of `id` must be > 0
        dummy_verified_contract.creation_transformations = [
            {"reason": "library", "type": "replace", "offset": 0, "id": ""}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")


class TestCborAuxdata:
    def test_valid_value(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "replace", "offset": 0, "id": "0"}
        ]
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_missing_key_type_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "offset": 0, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, 0, [], dict()], ids=["null", "number", "array", "object"])
    def test_invalid_key_type_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": value, "offset": 0, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_type_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "insert", "offset": 0, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_missing_key_offset_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "replace", "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, "", [], dict()], ids=["null", "string", "array", "object"])
    def test_invalid_key_offset_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "replace", "offset": value, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_offset_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                            dummy_compiled_contract, dummy_verified_contract):
        # The offset must be >= 0
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "replace", "offset": -1, "id": "0"}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_missing_key_id_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "replace", "offset": 0}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    @pytest.mark.parametrize("value", [None, 0, [], dict()], ids=["null", "number", "array", "object"])
    def test_invalid_key_id_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "replace", "offset": 0, "id": value}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")

    def test_invalid_key_id_value_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                        dummy_compiled_contract, dummy_verified_contract):
        # The length of `id` must be > 0
        dummy_verified_contract.creation_transformations = [
            {"reason": "cborAuxdata", "type": "replace", "offset": 0, "id": ""}
        ]
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_transformations_array")
