# Patterns

<!-- Agent-maintained. Builders read this before implementing. QA appends new patterns after approving tasks.
     Keep entries short: name, brief description, minimal code snippet. No duplicates. -->

---

<!-- Example entry format:

## API route handler
Handler shape used across all REST routes. Always validate input with Zod before processing.

```ts
export async function handleCreateItem(req: Request, res: Response) {
  const body = CreateItemSchema.parse(req.body);
  const result = await itemService.create(body);
  res.json({ data: result });
}
```

-->

## API handler with schema-first validation
Use schema validation at the boundary, then return structured success/error shapes.

```ts
export async function handleCreate(req: Request, res: Response) {
  const body = CreateItemSchema.parse(req.body);
  const item = await itemService.create(body);
  res.status(201).json({ data: item });
}
```

## UI async state matrix
Every async screen handles loading, error, empty, and success states explicitly.

```tsx
if (isLoading) return <ListSkeleton />;
if (error) return <ErrorState message="Could not load items." />;
if (items.length === 0) return <EmptyState title="No items yet" />;
return <ItemsList items={items} />;
```

## Test shape: happy path + edge path
For each unit, add at least one happy-path test and one edge/error test.

```ts
it("creates an item with valid input", async () => { /* ... */ });
it("returns validation error for missing title", async () => { /* ... */ });
```
