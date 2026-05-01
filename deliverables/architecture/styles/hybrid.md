# Profile: hybrid

## Description

A modular monolith with extraction-ready boundaries. Today you ship as a
monolith — one deploy, one database, fast iteration. Tomorrow when one
service gets too busy or too complex, you can lift it out into its own
microservice without rewriting business logic, because boundaries were
designed in from day one. Best fit for ~70% of real projects: teams who
say "we want microservices eventually" but shouldn't pay distributed-
systems cost yet. Speed of monolith now, optionality for later.

## Default tech additions

- **Backend framework:** NestJS (default) | Express + tRPC — same as monolith
- **Database:** Postgres — single instance, but each service owns its tables
- **Migration tool:** Prisma — single `schema.prisma`, organized by service
- **Cache:** Redis (recommended) — used through a shared interface so it's swappable
- **Job queue:** BullMQ (recommended) — same Redis used for cache
- **Events:** in-process EventEmitter today, BUT event names + schemas designed for Kafka tomorrow
- **API gateway:** none yet (one API surface) — gateway gets added when first service is extracted

## Folder structure

```
apps/<slug>/
├── services/                       # each service is its own folder (mirrors microservices layout)
│   ├── identity/
│   │   ├── src/
│   │   ├── ports.ts                # interfaces — extraction contract
│   │   ├── handlers.ts
│   │   ├── service.ts
│   │   ├── repository.ts
│   │   ├── events.ts               # event names + payload schemas
│   │   └── tests/
│   ├── booking/
│   │   ├── src/
│   │   ├── ports.ts
│   │   ├── handlers.ts
│   │   ├── service.ts
│   │   ├── repository.ts
│   │   ├── events.ts
│   │   └── tests/
│   ├── payment/
│   │   └── (same shape)
│   └── notification/
│       └── (same shape)
├── packages/                       # cross-service shared types only
│   └── shared/
│       ├── types/                  # used as INTERFACES, not implementations
│       └── ports/                  # composition-root contracts
├── prisma/
│   ├── schema.prisma               # ONE file, BUT each service owns its tables
│   │                               # Cross-service references by ID only — no FKs
│   └── migrations/
├── compose-root.ts                 # wires services together at boot — swap to extract
├── api/
│   └── gateway.ts                  # single HTTP entry, routes to service handlers
├── package.json                    # ONE package, ONE Dockerfile (single deploy today)
├── Dockerfile
└── README.md
```

## Database approach

**Single Postgres BUT with strict per-service ownership.** All tables in
one `schema.prisma`, but each service owns its own tables and other
services reference them by ID only — no foreign keys across service
boundaries.

- Tool: Prisma migrate (default)
- Tables grouped in `schema.prisma` by service (e.g. `// === booking ===` comment headers)
- Cross-service references: store the foreign ID as a column but DON'T add a `@relation` decorator
- This forces queries that need cross-service data to use service interfaces (ports), not SQL JOINs
- When you eventually extract a service, its tables move to a new DB without breaking anything
- No cross-service JOINs are written today, so extraction is mechanical not creative

## Communication style

**Through interface ports, never direct imports of other services'
internals.**

```ts
// services/booking/handlers.ts
import { NotificationPort } from '@shared/ports';

export async function createBooking(input, deps: { notify: NotificationPort }) {
  const booking = await db.bookings.insert(input);
  await deps.notify(input.userId, 'booked');   // through interface
  return booking;
}

// compose-root.ts (single composition point)
import { localNotify } from '@notification/local';     // today: in-process
// import { kafkaNotify } from '@notification/kafka';  // tomorrow: just swap
const deps = { notify: localNotify };
```

- Sync: through interface (`port`) — implementation passed at composition root
- Async: in-process EventEmitter today, but event names match what Kafka topics would be later
- Boundary discipline: STRICT — no service imports another service's internal files
- The phrase: "you probably won't extract them, but if you do, you can"

## Mermaid diagram patterns

### System architecture diagram

Outer subgraph per layer. Each service shown as its own node inside the
Domain layer. Subtle visual hint: nodes have rounded edges and dotted
internal arrows to suggest "could become independent". External boxes
(broker, cache) shown grayed-out / dashed because they're not deployed
yet but the contract for them is there.

### Database diagram

Single `erDiagram` block, but entities are grouped by service via
section comments. No `||--o{{` lines crossing service boundaries — only
ID references annotated as `# ref→users.id (service: identity)`.

### Infrastructure diagram

Same as monolith for now (one web + one API + one Postgres + Redis +
external integrations) but with a callout block: *"Migration path: each
service in `services/<name>/` can be extracted to its own deploy unit
when scale demands. Reference styles/microservices.md for the
extraction recipe."*
