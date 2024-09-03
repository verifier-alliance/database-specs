from helpers import *


class TestCreationValuesObjectConstraint:
    @pytest.fixture(scope='function', autouse=True)
    def setup(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
        dummy_code.insert(connection)
        dummy_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)
        dummy_contract_deployment.insert(connection, dummy_contract.id)
        dummy_compiled_contract.insert(
            connection, dummy_code.code_hash, dummy_code.code_hash)

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

    # This test shows that empty json objects instead of libraries are also allowed according to schema.
    # TODO: should they actually be allowed?
    def test_default_type_values(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values = dict({
            "constructorArguments": "0x1234",
            "libraries": {},
            "cborAuxdata": {}
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

    def test_unknown_field_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_values['unknown_key'] = dict({})
        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "creation_values_object")
