---
description: Frontend rules (adapt framework to the actual project)
globs: frontend/**, src/**, app/**, components/**, pages/**, lib/**, hooks/**
activation: glob
---
<!-- Example stack shown: Next.js + TypeScript. Swap for the project's actual
     frontend framework before copying into .agents/rules/. -->

Frontend rules:
- Prefer typed language for all frontend logic where the stack supports it.
- Keep components small, reusable, and focused.
- Keep presentation separate from business/data-fetching logic.
- Handle loading, error, and empty states explicitly.
- Preserve design and naming consistency.

Preferred structure — this is a CONTRACT, not a suggestion. Every AI tool working
on this repo (any teammate, any model) must place new files according to this
exact tree, and must read this tree before creating anything new rather than
inventing an alternative layout:

```
frontend/
├── app/                     # Routing/pages layer only (e.g. Next.js app router).
│                              # Compose components here, don't write heavy logic.
├── components/               # Reusable, presentation-only UI components.
│                              # No direct API calls inside components — they
│                              # receive data via props or hooks.
├── features/                  # Feature-specific groupings (component + hook +
│   │                            # types bundled per feature, e.g. features/auth/,
│   │                            # features/dashboard/).
├── hooks/                       # Reusable stateful logic (data fetching,
│                                  # subscriptions), returned to components.
├── lib/                          # Framework-agnostic utilities (formatting,
│                                  # validation helpers).
├── services/                      # Centralized API client functions — this is
│                                    # the ONLY place that calls backend
│                                    # endpoints. Never hardcode a fetch()/axios
│                                    # call inside a component.
├── types/                          # Shared TypeScript types/interfaces.
└── tests/                           # Mirrors the structure above.
```

Naming rule: a feature's component, hook, and service share a common prefix
(e.g. UserProfile.tsx in components/, useUserProfile.ts in hooks/,
userService.ts in services/) so any AI/teammate can find the matching pieces
without guessing.

State/data rules:
- Keep API clients centralized. Normalize repeated API access patterns.
- Handle auth state carefully. Validate critical inputs on both client and server.

Do not:
- Mix many responsibilities into one component.
- Hardcode API URLs in components.
- Duplicate UI patterns that should be shared.
