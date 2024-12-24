# JSON schemas

The VerA schema contains columns that are marked as JSONs.

Since it is not possible to add a JSON validator to the GCP Postgres instance, we define the JSON schemas here loosely and expect verifiers to follow them.

These are the current JSON fields:

`verified_contracts`:

- `creation_values`
- `creation_transformations`
- `runtime_values`
- `runtime_transformations`

`compiled_contracts`:

- `compiler_settings`
- `compilation_artifacts`
- `creation_code_artifacts`
- `runtime_code_artifacts`

## Rules

Apart from the specifications in each section below, the following rules apply to the JSON schemas:

- All hexadecimal value strings must be prefixed with `0x` such as addresses, constructor arguments etc.
- `offset` values correspond to bytes in the bytecode and not string indexes. So `offset: 1` for the bytecode "0xab46fd" is the first byte in the bytecode corresponds to start from `46`

## Transformations

A "transformation" on bytecode is a necessary change in the bytecode string to achieve the exact (on-chain) bytecode from a base bytecode. These changes don't effect the functionality of the bytecode. It includes:

- Constructor Arguments (only creation code)
- Immutable Variables (only runtime code)
- Libraries
- CBOR Auxdata
- Call Protection (only runtime code)

The transformations (where in the code and the reason) are stored in the `creation_` or `runtime_transformations` columns and the inserted values are stored in the `creation_` or `runtime_values` columns.

Example:

`runtime_transformations`:

```json
[
  {
    "id": "20",
    "type": "replace",
    "offset": 137, // in bytes
    "reason": "immutable"
  },
  {
    "id": "0",
    "type": "replace",
    "offset": 1002,
    "reason": "auxdata"
  }
]
```

`runtime_values`:

```json
{
  "immutables": {
    "20": "0x000000000000000000000000b5d83c2436ad54046d57cd48c00d619d702f3814"
  },
  "cborAuxdata": {
    "0": "0xa26469706673582212205817b060c918294cc8107069c4fd0a74dbfc35b0617214043887fe9d4e17a4a864736f6c634300081a0033"
  }
}
```

## verified_contracts

### creation_transformations

This object contains the transformation that will be applied to the creation bytecode.

The creation transformation can only contain these as `"reason"`s and `"type"`s:

- `{ "reason": "constructorArguments", "type": "insert", "offset": 999 }`
- `{ "reason": "cborAuxdata", "type": "replace", "offset": 123, id: "0" }` Needs an `id` since there can be multiple auxdata transformations e.g. factories.
- `{ "reason": "library", "type": "replace", "offset": 123, id: "sources/lib/MyLib.sol:MyLib" }`

Example:

```json
[
  {
    "id": "sources/lib/MyLib.sol:MyLib",
    "type": "replace",
    "offset": 582,
    "reason": "library"
  },
  {
    "id": "0",
    "type": "replace",
    "offset": 1269,
    "reason": "cborAuxdata"
  },
  {
    "type": "insert",
    "offset": 1322,
    "reason": "constructorArguments"
  }
]
```

### creation_values

This object contains the values that will be inserted/replaced in the creation bytecode.

The values can be `"cborAuxdata"`, `"library"`, `"constructorArguments"`.

```json
{
  "libraries": {
    "sources/lib/MyLib.sol:MyLib": "0x40b70a4904fad0ff86f8c901b231eac759a0ebb0"
  },
  "constructorArguments": "0x00000000000000000000000085fe79b998509b77bf10a8bd4001d58475d29386",
  "cborAuxdata": {
    "0": "0xa26469706673582212201c37bb166aa1bc4777a7471cda1bbba7ef75600cd859180fa30d503673b99f0264736f6c63430008190033"
  }
}
```

### runtime_transformation

Similar to `creation_transformation`. But runtime code does not contain constructor arguments but can have immutable variables and [call protection](https://docs.soliditylang.org/en/latest/contracts.html#call-protection-for-libraries).

The runtime transformations can only contain these as `"reason"`s and `"type"`s:

- `{ "reason": "cborAuxdata", "type": "replace", "offset": 123, id: "0" }` Needs an `id` since there can be multiple auxdata transformations e.g. factories.
- `{ "reason": "library", "type": "replace", "offset": 123, id: "contracts/order/OrderUtils.sol:OrderUtilsLib" }`
- `{ "reason": "immutable", "type": "replace", "offset": 999, id: "2473" }` Needs an `id` for referencing multiple times and there can be multiple immutable transformations. Solidity contracts have `"replace"` type, while Vyper ones have `"insert"` because they are appended to the runtime bytecode.
- `{ "reason": "callProtection", "type": "replace", "offset": 1 }`

Example 1:

```json
[
  {
    "id": "contracts/order/OrderUtils.sol:OrderUtilsLib",
    "type": "replace",
    "offset": 449,
    "reason": "library"
  },
  {
    "id": "2473",
    "type": "replace",
    "offset": 4339,
    "reason": "immutable"
  }
  {
    "id": "1",
    "type": "replace",
    "offset": 4682,
    "reason": "cborAuxdata"
  }
]
```

Example 2:

```json
[
  {
    "type": "replace",
    "offset": 1, // does not include the PUSH20 opcode 0x73 in the beginning
    "reason": "callProtection"
  }
]
```

### runtime_values

Example 1:

```json
{
  "libraries": {
    "contracts/order/OrderUtils.sol:OrderUtilsLib": "0x40b70a4904fad0ff86f8c901b231eac759a0ebb0"
  },
  "immutables": {
    "2473": "0x000000000000000000000000000000007f56768de3133034fa730a909003a165"
  },
  "cborAuxdata": {
    "1": "0xa26469706673582212201c37bb166aa1bc4777a7471cda1bbba7ef75600cd859180fa30d503673b99f0264736f6c63430008190033"
  }
}
```

Example 2:

```json
{
  "callProtection": "0x9deba23b95205127e906108f191a26f5d520896a" // just the 20 byte address without the 0x73 PUSH20 opcode in the beginning
}
```

## compiled_contracts

### compiler_settings

Compiler settings as passed to the compiler in JSON format

```json
{
  "libraries": {
    "contracts/order/IncreaseOrderUtils.sol": {
      "IncreaseOrderUtils": "0x3adeb5ce4b8a21f40c3900348dc35379320dcbff"
    }
  },
  "optimizer": {
    "runs": 200,
    "enabled": true
  },
  "outputSelection": {
    "*": {
      "*": ["evm.bytecode", "evm.deployedBytecode", "devdoc", "userdoc", "metadata", "abi"]
    },
    "contracts/order/OrderUtils.sol": {
      "OrderUtils": ["*"]
    }
  }
}
```

### compilation_artifacts

The fields from the compilation output JSON.

This object MUST contain the following fields. If a field is not output or available it MUST be set to `null`.

- `abi`
- `userdoc`
- `devdoc`
- `sources` - The AST identifiers of sources
- `storageLayout` - Only available after a certain Solidity version. If N/A set to `null`.

```json
{
  "abi": [...],
  "userdoc": {...},
  "devdoc": {...},
  "sources": {
    "contracts/proxy/ERC1967Proxy.sol": {
      "id": 0
    },
    "contracts/proxy/ERC1967Trans.sol": {
      "id": 1
    }
  },
  "storageLayout": {...}
}
```

### creation_code_artifacts

The fields under `evm.bytecode` of the compilation target contract in the compilation output JSON.

This object MUST contain the following fields, unless otherwise specified. If a required field is not available it MUST be set to `null`.

- `sourceMap` - In the newer versions of Vyper this is a JSON. For earlier versions and Solidity it's a string
- `linkReferences`
- `cborAuxdata` (optional) - the positions and the value of the CBOR auxdatas in the bytecode. This is not output by the compiler but has to be calculated by the verifier manually. If the verifier cannot calculate, the field isn't set in the object. If there are no CBOR auxdata, the field is set to `null`.

```json
{
  "sourceMap": "64:1990:0:-:0;;;443:1;408:36;;64:1990;;;;;;;;;;;;;;;;",
  "cborAuxdata": {
    "1": {
      "value": "0xa264697066735822122087fcd42abf4e96c83b36564d81df50fce05eca8d8a8ee3a87157b72b501c952d64736f6c63430008090033",
      "offset": 3853
    }
  },
  "linkReferences": {}
}
```

### runtime_code_artifacts

The fields under `evm.deployedBytecode` of the compilation target contract in the compilation output JSON.

In addition to the `creation_code_artifacts` fields, this object MUST contain the following fields. If a field is not output or available it MUST be set to `null`.

- <all fields from `creation_code_artifacts`>
- `immutableReferences`

```json
{
  "sourceMap": "1580:16227:21:-:0;;;;;;;;...",
  "cborAuxdata": {
    "1": {
      "value": "0xa26469706673582212209da9a9c431e04d0fe200fc9a3064e582d06894a511ee512e771f2ec24bb2f4f864736f6c63430008130033",
      "offset": 15660
    }
  },
  "linkReferences": {},
  "immutableReferences": {
    "2471": [
      {
        "start": 1830,
        "length": 32
      },
      ...
    ]
  }
}
```
