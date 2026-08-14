---
description: Frontend rules for SEC (Gradio UI mounted on FastAPI)
globs: app/frontend/**, app/main.py
activation: glob
---

Frontend rules:
- Build UI layout using a `gr.Blocks()` context to ensure complete design control.
- Organize components in a clean, multi-tab layout (`gr.Tab`) matching the three modes of the application:
  1. **Leaf Disease Diagnostic**
  2. **Flower Growth Stage Analysis**
  3. **Combined Ecological Report**
- Isolate the interface configuration. The Gradio interface layout must be built in `app/frontend/interface.py`, referencing helper layout elements from `app/frontend/components.py`.
- Do not make external API or prediction calls directly from layout event listeners; trigger Python functions that call the services in `app/services/`.

Preferred structure — this is a CONTRACT, not a suggestion. Every AI tool working on this repo (any teammate, any model) must place new files according to this exact tree:

```
app/
└── frontend/
    ├── interface.py     # Main Gradio application blocks and event routing
    ├── components.py    # Reusable Gradio components (headers, cards, layouts)
    └── assets/
        └── style.css    # Custom CSS overrides for sunflower-themed styling
```

Design & UX Guidelines:
- **Visuals**: Use a professional design system. Standard colors should feel premium, borrowing from a sunflower theme (soft yellows, forest greens, charcoal dark backgrounds).
- **Layouts**: Use `gr.Row` and `gr.Column` to group uploads next to outputs for logical user processing.
- **Feedback**: Display progress indicators on execution. Define explicit placeholder blocks for initial states before prediction is run.

Do not:
- Define inline layout configurations or inline CSS styling directly in `app/main.py`. Keep it clean.
- Bake large agronomic description strings inside the UI code. Read them from the static JSON tables via the data lookup logic.
