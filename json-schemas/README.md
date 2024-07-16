# JSON schemas

The VerA schema contains columns that are marked as JSONs.

Since it is not possible to add a JSON validator to the GCP Postgres instance, we define the JSON schemas here loosely and expect verifiers to follow them.

`verified_contracts`:

- `creation_values`
- `creation_transformations`
- `runtime_values`
- `runtime_transformations`

`compiled_contracts`:

- `sources`
- `compiler_settings`
- `compilation_artifacts`
- `creation_code_artifacts`
- `runtime_code_artifacts`

## Transformations

A "transformation" on bytecode is a necessary change in the bytecode string to achieve the exact (on-chain) bytecode from a base bytecode. These changes don't effect the functionality of the bytecode. It includes:

- Constuctor Arguments
- Immutable Variables
- Libraries
- CBOR Auxdata (CBOR metadata)
- Call Protection

The the transformations (where in the code and the reason) are stored in `creation_` or `runtime_transformations` column and the inserted values are stored in `creation_` or `runtime_values` column.

Example:

`runtime_transformations`:

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

`runtime_values`:

```json
[
  {
    "id": "20",
    "type": "replace",
    "offset": 137,
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

## verified_contracts

### creation_transformation

This object contains the transformation that will be applied to the creation bytecode.

The creation transformation can only contain these as `"reason"`s and `"type"`s:

- `{ "reason": "constructor", "type": "insert", "offset": 999 }`
- `{ "reason": "auxdata", "type": "replace", "offset": 123, id: "0" }` Needs an `id` since there can be multiple auxdata transformations e.g. factories.
- `{ "reason": "library", "type": "replace", "offset": 123, id: "__$757b5b171da3e0fe3a6c8dacd9aee462d3$__" }`

Example:

```json
[
  {
    "id": "__$757b5b171da3e0fe3a6c8dacd9aee462d3$__",
    "type": "replace",
    "offset": 582,
    "reason": "library"
  },
  {
    "id": "0",
    "type": "replace",
    "offset": 1269,
    "reason": "auxdata"
  },
  {
    "type": "insert",
    "offset": 1322,
    "reason": "constructor"
  }
]
```

### creation_values

This object contains the values that will be inserted/replaced in the creation bytecode.

The values can be `"cborAuxdata"`, `"libraries"`, `"constructorArguments"`.

```json
{
  "libraries": {
    "__$757b5b171da3e0fe3a6c8dacd9aee462d3$__": "0x40b70a4904fad0ff86f8c901b231eac759a0ebb0"
  },
  "constructorArguments": "0x00000000000000000000000085fe79b998509b77bf10a8bd4001d58475d29386",
  "cborAuxdata": {
    "0": "0xa26469706673582212201c37bb166aa1bc4777a7471cda1bbba7ef75600cd859180fa30d503673b99f0264736f6c63430008190033"
  }
}
```

### runtime_transformation

Similar to `creation_transformation`. But runtime code does not contain constructor arguments but can have immutable variables and [call protection](https://docs.soliditylang.org/en/latest/contracts.html#call-protection-for-libraries). Typically if a contract has a call protection, it's a library contract and will not have other transformations.

Example 1:

```json
[
  {
    "id": "__$757b5b171da3e0fe3a6c8dacd9aee462d3$__",
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
    "reason": "auxdata"
  }
]
```

Example 2:

```json
[
  {
    "type": "replace",
    "offset": 0,
    "reason": "call-protection"
  }
]
```

### runtime_values

Example 1:

```json
{
  "libraries": {
    "__$757b5b171da3e0fe3a6c8dacd9aee462d3$__": "0x40b70a4904fad0ff86f8c901b231eac759a0ebb0"
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
  "callProtection": "0x739deba23b95205127e906108f191a26f5d520896a"
}
```

## compiled_contracts

### sources

The source files in JSON format.

```json
{
  "contracts/ERC20.sol": "// SPDX-License-Identifier: MIT\npragma solidity >=0.8.11;\n\nimport Ownable from \"./utils/Ownable.sol\";\n\ncontract ERC20 is\n    Ownable...",
  "contracts/utils/Ownable.sol": "pragma solidity..."
}
```

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
