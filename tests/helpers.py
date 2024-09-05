import json
import os
import pytest
import psycopg2


def check_constraint_fails(function, constraint_name):
    with pytest.raises(psycopg2.errors.CheckViolation, match=fr'{constraint_name}'):
        function()


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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.id, self.compiler, self.version, self.language, self.name, self.fully_qualified_name,
                  json.dumps(self.compiler_settings), json.dumps(
                      self.compilation_artifacts), creation_code_hash, json.dumps(self.creation_code_artifacts),
                  runtime_code_hash, json.dumps(self.runtime_code_artifacts)))


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
def dummy_compiled_contract(dummy_code):
    return CompiledContract.dummy()


def initialize_schema(connection):
    with open('./database.sql', 'r') as schema_file:
        schema = schema_file.read()

    with connection.cursor() as cursor:
        cursor.execute(schema)
