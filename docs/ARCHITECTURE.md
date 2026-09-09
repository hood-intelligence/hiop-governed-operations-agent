# Architecture

```mermaid
flowchart LR
  C[Customer request] --> S[Strands operations clerk]
  S --> I[investigate_customer]
  I --> L[Demo ledger]
  S --> A[request_refund_authority]
  A --> N[Narwhal identity]
  N --> M[Meerkat context]
  M --> CR[CRUSHIA effect authority]
  CR -->|PERMIT| G[Execution gate]
  CR -->|PERMIT_WITH_APPROVAL| H[Human approval fact]
  CR -->|DENY| X[No dispatch]
  H --> CR2[Fresh CRUSHIA]
  CR2 -->|PERMIT| G
  G --> E[issue_refund]
  E --> F[Fossil evidence]
  CR --> F
  H --> F
```

## Decision table (this demo)

| Case | Amount | Tenant | CRUSHIA | Dispatch |
|---|---|---|---|---|
| Maya duplicate seat | $20 | hood-ops | PERMIT | yes |
| Jordan duplicate contract | $750 | hood-ops | PERMIT_WITH_APPROVAL | no, until fresh PERMIT |
| Other Tenant LLC | $20 | foreign | DENY | no |

## Strands

The clerk is a `strands.Agent` with four tools. Tools never move money except
`execute_refund`, which can only run with a HIOP permit token.
