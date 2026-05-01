# Stack Guidance Template — Next.js + Prisma + Postgres

> Copy this file to `memory/STACK-GUIDANCE.md` when `import docs` detects
> this stack. Edit any section to reflect project-specific choices.

## Status

- Template: `nextjs-prisma-postgres`
- Source of truth: `SCOPE.md` sections 2 and 3
- If SCOPE changes materially, regenerate this file via `import docs`.

## Stack summary

- Frontend: Next.js 14 App Router, React 18, TypeScript strict
- Backend: Next.js route handlers (`app/api/*`), Node 20
- Database: PostgreSQL 16
- ORM: Prisma 5 (migrate + client)
- Auth: NextAuth v5, HttpOnly session cookie
- Styling: Tailwind CSS + shadcn/ui
- Testing: Vitest (unit), Playwright (e2e smoke)

## Architectural defaults

- Server Components by default. Opt in to `"use client"` only when
  interactivity demands it (forms, stateful widgets, drag-drop, charts).
- Route handlers are thin: parse + validate → call a service → shape
  response. No business logic inside `app/api/**/route.ts`.
- Service layer (`src/services/*`) holds business logic. Services never
  reference `req` / `res` / `cookies`.
- Data access is centralized in `src/db/` with one Prisma client instance.
- No direct Prisma calls from Server Components; go through a service or a
  typed "queries" module that wraps Prisma.

## File and module conventions

```
src/
  app/
    (marketing)/...        // unauthenticated public marketing pages
    (auth)/...             // sign-in / sign-up / magic-link routes
    (app)/...              // authenticated product routes
    api/
      <feature>/route.ts   // route handlers grouped by feature
  services/
    <feature>.ts
  db/
    client.ts              // prisma client singleton
    queries/<feature>.ts   // typed query helpers
    schema.prisma
  models/
    <feature>.ts           // zod schemas, shared types
  ui/
    components/            // reusable components
    primitives/            // shadcn/ui wrappers
  lib/
    auth.ts                // nextauth config
    logger.ts              // pino or equivalent
    config.ts              // env parsing
  tests/
    unit/
    e2e/
```

Naming: route segments `kebab-case`. Components `PascalCase`. Service files
`camelCase`. One feature = one service file + one queries file + one route
group.

## Data, state, and API guidance

- Validate every route handler input with Zod. Return
  `{ error: { code, message } }` for 4xx and 5xx.
- Server Actions are acceptable for same-feature mutations but must still
  call through `src/services/*`. Do not inline Prisma in an action.
- Use React Query (`@tanstack/react-query`) only in Client Components that
  need client-side refetch. Prefer Server Component data fetching elsewhere.
- Never expose Prisma entities directly. Map to DTOs in `models/`.

## UI and UX guidance

- Start from shadcn/ui primitives. Extend them in `src/ui/primitives/`.
  Do not fork shadcn files outside `src/ui/primitives/`.
- Every data view handles four states explicitly: loading, empty, error,
  success. Use `Suspense` + `error.tsx` where appropriate.
- Forms: `react-hook-form` + `zodResolver`. Error display is inline per
  field; global errors use the Toast primitive.
- Accessibility: all interactive elements reachable via keyboard. Use
  `@radix-ui/react-*` primitives underneath shadcn for correct a11y.

## Testing guidance

- Unit test services and route handlers with Vitest. Mock Prisma with a
  shared `prismaMock` fixture.
- Co-locate unit tests as `*.test.ts` next to the source.
- One Playwright smoke per user-facing flow defined in `SCOPE.md`'s
  feature `User flow` section.
- Fixture data lives in `tests/fixtures/`. Never commit real PII.

## Avoid

- Business logic in route handlers or server actions.
- Direct Prisma queries inside Server Components.
- Forking shadcn files across the tree — fork them only in
  `src/ui/primitives/`.
- `useEffect` for data fetching on the server side.
- `any` types. Prefer `unknown` then narrow with Zod.
- Mixing session cookies with JWT in the client — pick one (NextAuth
  session cookie is the default for this stack).
