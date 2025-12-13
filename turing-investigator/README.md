# TuringResolve™ Investigator UI

**Authoritative outcomes with full history and override lineage**

## Overview

The TuringResolve Investigator UI is a web-based interface for viewing and managing resolve timelines in the TuringMachines identity verification system.

### Key Features

- ✅ **Resolve Timeline Viewer**: View complete history of all resolves for a workflow
- ✅ **Override Functionality**: Create new resolves that supersede previous ones
- ✅ **Immutable History**: All resolves are preserved with full lineage
- ✅ **Event-Sourced Architecture**: Reads only from `decision.finalised` events
- ✅ **Authority Compliance**: UI cannot bypass backend authority

## Architecture Principles

### Immutable Resolves
- Overrides **never edit** existing resolves
- Overrides **always create** a new resolve
- UI **cannot** "edit" or "delete" history
- Override **requires** an explicit reason

### Event-Sourced Authority
- UI submits `override.applied` events (not mutations)
- Backend authority emits authoritative `decision.finalised` events
- Timeline reads only from authoritative events
- No silent edits, no ambiguity

## Getting Started

### Prerequisites
- Node.js 18+
- pnpm (or npm/yarn)

### Installation

```bash
cd turing-investigator/ui
pnpm install
```

### Development

```bash
# Start dev server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview
```

### Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://127.0.0.1:8100
```

## Usage

### Viewing Resolve Timeline

1. Enter a workflow ID (e.g., `wf_test_001`)
2. Click "Load Resolve History"
3. View the complete timeline with:
   - Current resolve (highlighted)
   - Historical resolves
   - Override lineage
   - Authority information

### Overriding a Resolve

1. Click "🔁 Override Resolve"
2. Select new outcome (approve/review/decline)
3. Provide a mandatory reason
4. Click "Override Resolve"
5. Timeline refreshes automatically with the new resolve

## API Integration

### Endpoints Used

- **GET** `/v1/investigator/workflows/{workflow_id}/decisions`
  - Fetches resolve timeline
  - Returns all `decision.finalised` events

- **POST** `/v1/orchestrate/event`
  - Submits `override.applied` event
  - Backend processes and emits new `decision.finalised`

## Components

### `App.tsx`
Main application component with workflow ID input and override button.

### `DecisionTimeline.tsx`
Timeline viewer component that displays all resolves with lineage.

### `OverrideResolveModal.tsx`
Modal dialog for submitting override requests.

### `api/overrides.ts`
API client for submitting override events.

## Design Decisions

### Why Events, Not Mutations?

The UI submits **events** (`override.applied`), not direct mutations. This ensures:
- Backend authority is always enforced
- UI cannot bypass validation
- All changes are auditable
- System remains event-sourced

### Why Immutable History?

Preserving all resolves ensures:
- Complete audit trail
- Regulatory compliance
- Dispute resolution
- Override accountability

## Technology Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: React hooks
- **API Client**: Fetch API

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) in the root of the repository.

## License

See [LICENSE](../LICENSE) in the root of the repository.

---

**TuringResolve™** — Single Source of Truth
