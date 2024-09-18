from helpers import *


@pytest.fixture(scope='function', autouse=True)
def setup(connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract):
    dummy_code.insert(connection)
    dummy_contract.insert(
        connection, dummy_code.code_hash, dummy_code.code_hash)
    dummy_contract_deployment.insert(connection, dummy_contract.id)
    dummy_compiled_contract.insert(
        connection, dummy_code.code_hash, dummy_code.code_hash)


class TestTable:
    def test_both_matches_are_true(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_match = True
        dummy_verified_contract.creation_values = dict()
        dummy_verified_contract.creation_transformations = []
        dummy_verified_contract.creation_metadata_match = True

        dummy_verified_contract.runtime_match = True
        dummy_verified_contract.runtime_values = dict()
        dummy_verified_contract.runtime_transformations = []
        dummy_verified_contract.runtime_metadata_match = True

        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_creation_match_only_is_true(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_match = True
        dummy_verified_contract.creation_values = dict()
        dummy_verified_contract.creation_transformations = []
        dummy_verified_contract.creation_metadata_match = True

        dummy_verified_contract.runtime_match = False
        dummy_verified_contract.runtime_values = Null
        dummy_verified_contract.runtime_transformations = Null
        dummy_verified_contract.runtime_metadata_match = Null

        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_runtime_match_only_is_true(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_match = False
        dummy_verified_contract.creation_values = Null
        dummy_verified_contract.creation_transformations = Null
        dummy_verified_contract.creation_metadata_match = Null

        dummy_verified_contract.runtime_match = True
        dummy_verified_contract.runtime_values = dict()
        dummy_verified_contract.runtime_transformations = []
        dummy_verified_contract.runtime_metadata_match = True

        dummy_verified_contract.insert(
            connection, dummy_contract_deployment.id, dummy_compiled_contract.id)

    def test_false_both_creation_and_runtime_matches_fails(self, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_match = False
        dummy_verified_contract.creation_values = Null
        dummy_verified_contract.creation_transformations = Null
        dummy_verified_contract.creation_metadata_match = Null

        dummy_verified_contract.runtime_match = False
        dummy_verified_contract.runtime_values = Null
        dummy_verified_contract.runtime_transformations = Null
        dummy_verified_contract.runtime_metadata_match = Null

        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "verified_contracts_match_exists"
        )

    @pytest.mark.parametrize("field", ["creation_values", "creation_transformations", "creation_metadata_match"])
    def test_creation_match_without_details_fails(self, field, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_match = True
        dummy_verified_contract.creation_values = dict()
        dummy_verified_contract.creation_transformations = []
        dummy_verified_contract.creation_metadata_match = True

        dummy_verified_contract.__setattr__(field, Null)

        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "verified_contracts_creation_match_integrity"
        )

    @pytest.mark.parametrize("field,value", [("creation_values", dict()), ("creation_transformations", []), ("creation_metadata_match", False)])
    def test_no_creation_match_with_details_fails(self, field, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.creation_match = False
        dummy_verified_contract.creation_values = Null
        dummy_verified_contract.creation_transformations = Null
        dummy_verified_contract.creation_metadata_match = Null

        dummy_verified_contract.__setattr__(field, value)

        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "verified_contracts_creation_match_integrity"
        )

    @pytest.mark.parametrize("field", ["runtime_values", "runtime_transformations", "runtime_metadata_match"])
    def test_runtime_match_without_details_fails(self, field, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.runtime_match = True
        dummy_verified_contract.runtime_values = dict()
        dummy_verified_contract.runtime_transformations = []
        dummy_verified_contract.runtime_metadata_match = True

        dummy_verified_contract.__setattr__(field, Null)

        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "verified_contracts_runtime_match_integrity"
        )

    @pytest.mark.parametrize("field,value", [("runtime_values", dict()), ("runtime_transformations", []), ("runtime_metadata_match", False)])
    def test_no_runtime_match_with_details_fails(self, field, value, connection, dummy_code, dummy_contract, dummy_contract_deployment, dummy_compiled_contract, dummy_verified_contract):
        dummy_verified_contract.runtime_match = False
        dummy_verified_contract.runtime_values = Null
        dummy_verified_contract.runtime_transformations = Null
        dummy_verified_contract.runtime_metadata_match = Null

        dummy_verified_contract.__setattr__(field, value)

        check_constraint_fails(
            lambda: dummy_verified_contract.insert(
                connection, dummy_contract_deployment.id, dummy_compiled_contract.id),
            "verified_contracts_runtime_match_integrity"
        )
