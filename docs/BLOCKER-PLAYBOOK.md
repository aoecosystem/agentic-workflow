# Blocker Playbook

Use this playbook whenever a task cannot continue safely. The goal is deterministic handling and fast escalation.

---

## Required blocker note format

When marking `Status: blocked`, include:

- blocker type
- exact reason
- task/dependency reference (if applicable)
- what was tried
- specific user question or required input

Template:

`- QA notes: BLOCKED. Type: <type>. Reason: <specific reason>. Tried: <steps>. Need: <clear question/input>.`

---

## Blocker types and handling

### 1) Dependency blocked

- **Set status:** `blocked`
- **Reason format:** `Depends on TASK-XYZ which is not done`
- **Escalate:** ask whether to reprioritize or wait for dependency resolution
- **Retry when:** dependency task is `done` (then move `blocked -> pending`)

### 2) Ambiguous scope/spec

- **Set status:** `blocked`
- **Reason format:** include the exact unclear sentence from `SCOPE.md`
- **Escalate:** ask one focused clarification question
- **Retry when:** clarification is provided and task acceptance criteria are updated if needed

### 3) MCP or external source unreachable

- **Set status:** `blocked`
- **Reason format:** include URL/tool name and error summary
- **Escalate:** ask user to confirm access/URL or provide replacement source
- **Retry when:** source is reachable or alternate source is approved

### 4) Persistent verification failure

- **Set status:** `blocked` after two failed fix attempts
- **Reason format:** list failing gate(s) and attempted fixes
- **Escalate:** ask user for direction (accept scope cut, provide fixture/data, or adjust requirements)
- **Retry when:** user provides direction and failure cause is addressed

---

## Escalation message examples

- `Task is blocked by TASK-003 dependency. Should I wait, or reprioritize a different ready task?`
- `Scope is ambiguous in SCOPE.md: "<quoted sentence>". Should this endpoint be public or authenticated?`
- `MCP URL is unreachable: <url>. Can you verify access or provide a replacement source?`
- `Verification still fails after two attempts in <file>. Should I narrow scope or continue with your preferred fix strategy?`
