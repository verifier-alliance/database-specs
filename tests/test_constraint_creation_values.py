from helpers import *


def setup(connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
    dummy_code.insert(connection)
    dummy_contract.insert(
        connection, dummy_code.code_hash, dummy_code.code_hash)
    dummy_contract_deployment.insert(connection, dummy_contract.id)
    dummy_compiled_contract.insert(
        connection, dummy_code.code_hash, dummy_code.code_hash)


class TestObject:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
        setup(connection, dummy_code, dummy_contract,
              dummy_contract_deployment, dummy_compiled_contract)

    def test_no_fields_are_required(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({})
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_expected_type_values(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": "0x1234",
            "libraries": {"file1:lib1": "0x4000000000000000000000000000000000000000"},
            "cborAuxdata": {"1": "0x00000000000000000000000000000000000000000000000000000000000000000000000000"}
        })
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_invalid_json_type_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = "just a string"
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_immutables_field_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values["immutables"] = dict({})
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_call_protection_field_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values["callProtection"] = "0x4000000000000000000000000000000000000000"
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_unknown_field_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values['unknown_key'] = dict({})
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")


########## Tests constructorArguments field constraints ##########
class TestObjectConstructorArguments:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
        setup(connection, dummy_code, dummy_contract,
              dummy_contract_deployment, dummy_compiled_contract)

    def test_valid_field_value(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": "0x1234"
        })
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    @pytest.mark.parametrize("value", [None, [], dict()], ids=["null", "array", "object"])
    def test_invalid_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": value
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_without_0x_prefix_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": "1234"
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_not_valid_hex_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": "0xqwer"
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_empty_hex_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": "0x"
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_odd_length_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": "0x123"
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

########## Tests libraries field constraints ##########


class TestObjectLibraries:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
        setup(connection, dummy_code, dummy_contract,
              dummy_contract_deployment, dummy_compiled_contract)

    def test_valid_field_value(self, connection, dummy_code, dummy_contract,
                               dummy_contract_deployment, dummy_compiled_contract,
                               dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": {"file1:lib1": "0x4000000000000000000000000000000000000000"}
        })
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_empty_object(self, connection, dummy_code, dummy_contract,
                          dummy_contract_deployment, dummy_compiled_contract,
                          dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": {}
        })
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    @pytest.mark.parametrize("value", [None, [], ""], ids=["null", "array", "string"])
    def test_invalid_type_fails(self, value, connection, dummy_code, dummy_contract,
                                dummy_contract_deployment, dummy_compiled_contract,
                                dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": value
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    @pytest.mark.parametrize("value", [None, [], dict({})], ids=["null", "array", "object"])
    def test_additional_properties_with_invalid_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                                           dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": {"file1:lib1": value}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_values_without_0x_prefix_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                            dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": {"file1:lib1": "4000000000000000000000000000000000000000000000000"}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_values_not_valid_hex_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                        dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": {"file1:lib1": "0xqw00000000000000000000000000000000000000000000000"}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_values_not_20_bytes_hex_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                           dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": {"file1:lib1": "0x1000000000"}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_values_one_fail_all_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                       dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "libraries": {
                "file1:lib1": "4000000000000000000000000000000000000000000000000",
                "file2:lib2": "0x4000000000000000000000000000000000000000000000000"
            }
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

########## Tests cborAuxdata field constraints ##########


class TestObjectCborAuxdata:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
        setup(connection, dummy_code, dummy_contract,
              dummy_contract_deployment, dummy_compiled_contract)

    def test_valid_field_value(self, connection, dummy_code, dummy_contract,
                               dummy_contract_deployment, dummy_compiled_contract,
                               dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {"1": "0x00000000000000000000000000000000000000000000000000000000000000000000000000"}
        })
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_empty_object(self, connection, dummy_code, dummy_contract,
                          dummy_contract_deployment, dummy_compiled_contract,
                          dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {}
        })
        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    @pytest.mark.parametrize("value", [None, [], ""], ids=["null", "array", "string"])
    def test_invalid_type_fails(self, value, connection, dummy_code, dummy_contract,
                                dummy_contract_deployment, dummy_compiled_contract,
                                dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": value
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    @pytest.mark.parametrize("value", [None, [], dict({})], ids=["null", "array", "object"])
    def test_additional_properties_with_invalid_type_fails(self, value, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                                           dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {"1": value}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_values_without_0x_prefix_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                            dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {"1": "00000000000000000000000000000000000000000000000000000000000000000000000000"}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_values_not_valid_hex_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                        dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {"1": "0xqwer0000000000000000000000000000000000000000000000000000000000000000000000"}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_empty_hex_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {"1": "0x"}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_odd_length_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {"1": "0x123"}
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")

    def test_values_one_fail_all_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment,
                                       dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "cborAuxdata": {
                "1": "0x00000000000000000000000000000000000000000000000000000000000000000000000000",
                "2": "00000000000000000000000000000000000000000000000000000000000000000000000000"
            }
        })
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")
