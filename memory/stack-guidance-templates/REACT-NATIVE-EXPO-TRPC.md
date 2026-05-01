# Stack Guidance Template — React Native (Expo) + tRPC + Postgres

> Copy this file to `memory/STACK-GUIDANCE.md` when `import docs` detects
> this stack. Edit any section to reflect project-specific choices.

## Status

- Template: `react-native-expo-trpc`
- Source of truth: `SCOPE.md` sections 2 and 3
- If SCOPE changes materially, regenerate this file via `import docs`.

## Stack summary

- Mobile app: React Native + Expo SDK 50, TypeScript strict
- Navigation: Expo Router
- API layer: tRPC v11 over fetch, shared router definitions
- Backend: Node 20 server (Fastify or Next.js route handler host)
- Database: PostgreSQL 16 via Prisma 5
- Auth: session token stored in `expo-secure-store`, rotated on refresh
- Styling: NativeWind (Tailwind for React Native)
- Testing: Jest + React Native Testing Library (unit), Detox (e2e smoke)

## Architectural defaults

- Monorepo with pnpm workspaces:
  - `apps/mobile` — Expo app
  - `apps/api` — tRPC server
  - `packages/api` — tRPC router + Zod schemas (shared)
  - `packages/db` — Prisma schema + client
  - `packages/ui` — shared components (rare)
- tRPC router is the only contract. No REST on the side.
- All procedures are typed end-to-end. Never hand-roll a `fetch` in the app.
- Zod schemas live in `packages/api/schemas/` and are imported by both the
  router and the app forms.

## File and module conventions

```
apps/
  mobile/
    app/                   // Expo Router routes
      (auth)/login.tsx
      (app)/index.tsx
    src/
      screens/             // screen-level components (complex screens)
      components/          // reusable UI
      hooks/               // app-specific hooks
      lib/
        trpc.ts            // tRPC client
        secure-store.ts    // session storage
        logger.ts
  api/
    src/
      routers/             // tRPC routers per feature
      services/            // business logic
      db.ts                // Prisma client
packages/
  api/
    src/
      router.ts            // root router
      schemas/             // Zod schemas shared with app
  db/
    schema.prisma
```

Naming: screens `PascalCase.tsx`. Hooks `useXxx`. Routers `featureRouter`.

## Data, state, and API guidance

- tRPC + React Query. Use `useQuery` for reads, `useMutation` for writes.
  Invalidate relevant query keys after mutations — never force a full
  re-render.
- Optimistic updates only when the acceptance criteria ask for them.
- Session token retrieved from `expo-secure-store` on app start and injected
  into the tRPC `headers` function.
- 401 from tRPC triggers a logout flow handled by a single interceptor
  (not scattered across screens).

## UI and UX guidance

- Use NativeWind (`className="..."`). Avoid inline `StyleSheet.create`
  unless NativeWind cannot express the style.
- Safe-area: every screen wraps its root in `SafeAreaView` (from
  `react-native-safe-area-context`), not the native component.
- Lists: `FlashList` from Shopify for any list that can grow past 50
  items. Use `FlatList` only for small static lists.
- Never build status bars / notches / home indicators inside app screens.
  Treat Figma device previews as framing only.
- All four states for data: loading, empty, error, success. Empty states
  must offer an action ("Add your first task") when the user can resolve
  the empty state.
- Accessibility: `accessibilityLabel`, `accessibilityRole`, and
  `accessibilityState` on every interactive element.

## Testing guidance

- Unit tests: Jest + React Native Testing Library. Test behavior (screen
  renders X when tRPC returns Y), not implementation.
- Mock tRPC with `@trpc/react-query/testing` utilities.
- Snapshot tests are permitted only for pure presentational components.
- Detox smoke per major user flow defined in `SCOPE.md`.

## Avoid

- Bypass tRPC with a raw `fetch` — breaks type safety and auth.
- Store the session token in AsyncStorage (not encrypted) — must be
  `expo-secure-store`.
- Mix navigation paradigms — stay on Expo Router; do not introduce
  `@react-navigation/native` directly.
- Reintroduce `StyleSheet.create` where NativeWind works.
- Recreate device chrome (status bar, notch, home indicator) inside a
  screen — the OS provides it.
- `any` types. Prefer `unknown` then narrow with Zod.
