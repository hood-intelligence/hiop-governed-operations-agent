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
| OTC wall sign | $20 | hood-ops | PERMIT | yes — issues NH-SGN-… |
| Commercial building BLD-2026-08441 | **$7,600** | hood-ops | PERMIT_WITH_APPROVAL | no, until building official + fresh PERMIT |
| Riverside Holdings | $7,600 | other-jurisdiction | DENY | no |

## Strands

The clerk is a `strands.Agent` with four tools. Tools never move money except
`execute_refund`, which can only run with a HIOP permit token.
