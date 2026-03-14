# Axiom Core Skills

Essential agent node types for Axiom AI agents.

## Included Node Types

### Triggers
- `webhook` - Trigger via HTTP webhook
- `cron` - Run on a schedule
- `manual` - Manual trigger

### Control Flow
- `if` - Conditional branching
- `switch` - Multi-way branching
- `delay` - Wait for duration

### Actions
- `http` - Make HTTP requests
- `code` - Execute Python code
- `ai` - AI/LLM model calls
- `invoke_agent` - Invoke another agent (A2A)

### Data Operations
- `transform` - Transform data
- `set` - Set variables
- `merge` - Merge data
- `filter` - Filter arrays
- `sort` - Sort arrays
- `aggregate` - Aggregate values
- `split` - Split arrays
- `join` - Join arrays
- `loop` - Iterate over arrays

### Communication
- `slack` - Send Slack messages
- `discord` - Send Discord messages
- `teams` - Send MS Teams messages
- `email` - Send emails

### Tools
- `tool_pgvector` - Vector database operations
- `tool_debug` - Debug output
- `tool_memory` - Memory operations

### Response
- `webhook_response` - Send HTTP response (sync webhook mode)

## Usage

This skill is automatically loaded by Atlas as a system skill when configured via `SYSTEM_SKILL_REPOS`.

## License

Apache-2.0