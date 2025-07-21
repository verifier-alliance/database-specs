import json
import os
import pytest
import psycopg2
from dataclasses import dataclass


def check_constraint_fails(function, constraint_name):
    with pytest.raises(psycopg2.errors.CheckViolation, match=fr'{constraint_name}'):
        function()


@dataclass
class Null:
    def __init__(self):
        pass


class Code:
    code_hash = b''
    code_hash_keccak = b''
    code = b''

    @staticmethod
    def dummy():
        instance = Code()
        instance.code_hash = bytes.fromhex(
            'b2ed992186a5cb19f6668aade821f502c1d00970dfd0e35128d51bac4649916c')
        instance.code_hash_keccak = bytes.fromhex(
            '30ca65d5da355227c97ff836c9c6719af9d3835fc6bc72bddc50eeecc1bb2b25')
        instance.code = bytes.fromhex('12345678')
        return instance

    def insert(self, connection):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO code (code_hash, code_hash_keccak, code)
                VALUES (%s, %s, %s)
            """, (self.code_hash, self.code_hash_keccak, self.code))


class Contract:
    id = ""

    @staticmethod
    def dummy():
        instance = Contract()
        instance.id = 'df8fd690-70a8-4dd8-b42b-5c12e5d05dbe'
        return instance

    def insert(self, connection, creation_code_hash, runtime_code_hash):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO contracts (id, creation_code_hash, runtime_code_hash)
                VALUES (%s, %s, %s)
            """, (self.id, creation_code_hash, runtime_code_hash))


class ContractDeployment:
    id = ""
    chain_id = 0
    address = b''
    transaction_hash = b''
    block_number = 0
    transaction_index = 0
    deployer = b''

    @staticmethod
    def dummy():
        instance = ContractDeployment()
        instance.id = '42d20697-5427-4130-adbd-97daab2b2dd1'
        instance.chain_id = 1
        instance.address = bytes.fromhex(
            '0000000000000000000000000000000000000000')
        instance.transaction_hash = bytes.fromhex(
            '0000000000000000000000000000000000000000000000000000000000000000')
        instance.block_number = -1
        instance.transaction_index = -1
        instance.deployer = '0000000000000000000000000000000000000000'
        return instance

    def insert(self, connection, contract_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO contract_deployments (
                    id, chain_id, address, transaction_hash,
                    block_number, transaction_index, deployer, contract_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.id, self.chain_id, self.address, self.transaction_hash,
                  self.block_number, self.transaction_index, self.deployer, contract_id))


class CompiledContract:
    id = ""
    compiler = ""
    version = ""
    language = ""
    name = ""
    fully_qualified_name = ""
    compiler_settings = dict()
    compilation_artifacts = dict()
    creation_code_artifacts = dict()
    runtime_code_artifacts = dict()

    @staticmethod
    def dummy():
        instance = CompiledContract()
        instance.id = 'e405ffd2-fcbe-46ad-aedb-da320af35e46'
        instance.compilation_artifacts = dict({
            "abi": None,
            "userdoc": None,
            "devdoc": None,
            "sources": None,
            "storageLayout": None
        })
        instance.creation_code_artifacts = dict({
            "sourceMap": None,
            "linkReferences": None,
            "cborAuxdata": None
        })
        instance.runtime_code_artifacts = dict({
            "sourceMap": None,
            "linkReferences": None,
            "immutableReferences": None,
            "cborAuxdata": None
        })

        return instance

    def insert(self, connection, creation_code_hash, runtime_code_hash):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO compiled_contracts (
                    id, compiler, version, language, name, fully_qualified_name, 
                    compiler_settings, compilation_artifacts, creation_code_hash, creation_code_artifacts,
                    runtime_code_hash, runtime_code_artifacts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.id, self.compiler, self.version, self.language, self.name, self.fully_qualified_name,
                  json.dumps(self.compiler_settings), json.dumps(
                      self.compilation_artifacts), creation_code_hash, json.dumps(self.creation_code_artifacts),
                  runtime_code_hash, json.dumps(self.runtime_code_artifacts)))


class VerifiedContract:
    id = ""
    creation_match = False
    creation_values = Null
    creation_transformations = Null
    creation_metadata_match = Null
    runtime_match = False
    runtime_values = Null
    runtime_transformations = Null
    runtime_metadata_match = Null

    @staticmethod
    def dummy():
        instance = VerifiedContract()
        instance.id = 1
        instance.creation_match = True
        instance.creation_values = dict()
        instance.creation_transformations = []
        instance.creation_metadata_match = True
        instance.runtime_match = True
        instance.runtime_values = dict()
        instance.runtime_transformations = []
        instance.runtime_metadata_match = True

        return instance

    def insert(self, connection, deployment_id, compilation_id):
        query_columns = "id, deployment_id, compilation_id, creation_match, runtime_match"
        values = [self.id, deployment_id, compilation_id,
                  self.creation_match, self.runtime_match]

        if self.creation_values != Null:
            query_columns += ", creation_values"
            values.append(json.dumps(self.creation_values))
        if self.creation_transformations != Null:
            query_columns += ", creation_transformations"
            values.append(json.dumps(self.creation_transformations))
        if self.creation_metadata_match != Null:
            query_columns += ", creation_metadata_match"
            values.append(self.creation_metadata_match)

        if self.runtime_values != Null:
            query_columns += ", runtime_values"
            values.append(json.dumps(self.runtime_values))
        if self.runtime_transformations != Null:
            query_columns += ", runtime_transformations"
            values.append(json.dumps(self.runtime_transformations))
        if self.runtime_metadata_match != Null:
            query_columns += ", runtime_metadata_match"
            values.append(self.runtime_metadata_match)

        query_values = ", ".join(["%s"] * len(values))
        with connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO verified_contracts ({query_columns})
                VALUES ({query_values})
            """, values)


@pytest.fixture(scope="function", autouse=True)
def initialize(connection):
    initialize_schema(connection)
    yield
    connection.rollback()


@pytest.fixture(scope="function")
def connection():
    database = os.environ.get("DATABASE_NAME", "postgres")
    user = os.environ.get("DATABASE_USER", "postgres")
    password = os.environ.get("DATABASE_PASSWORD", "password")
    host = os.environ.get("DATABASE_HOST", "localhost")
    port = os.environ.get("DATABASE_PORT", "5432")
    return psycopg2.connect(database=database, user=user, host=host, password=password,
                            port=port)


@pytest.fixture
def dummy_code() -> Code:
    return Code.dummy()


@pytest.fixture
def dummy_contract() -> Contract:
    return Contract.dummy()


@pytest.fixture
def dummy_contract_deployment():
    return ContractDeployment.dummy()


@pytest.fixture
def dummy_compiled_contract():
    return CompiledContract.dummy()


@pytest.fixture
def dummy_verified_contract():
    return VerifiedContract.dummy()


def initialize_schema(connection, schema_name="public"):
    with open('./database.sql', 'r') as schema_file:
        schema = schema_file.read()

    with connection.cursor() as cursor:
        cursor.execute(schema)
        # Set the schema search path because `database.sql` resets it
        cursor.execute(f"SET search_path = {schema_name}")
