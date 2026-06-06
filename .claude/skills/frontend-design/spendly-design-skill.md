---
name: spendly-ui
description: >
  Build production-ready UI pages and components for the Spendly expense tracker app.
  Trigger this skill automatically whenever the user says:
  - "design the ... page"
  - "create UI for ..."
  - "build component for ..."
  - "redesign ..."
  - "add a ... screen"
  - "make the ... section"
  ... or any request to create or update a visual part of the Spendly app.
  Always use this skill for ANY Spendly UI/frontend work — even if the request seems simple.
  Never produce generic UI; always match Spendly's established design system.
---

# Spendly UI Skill

You are building UI for **Spendly** — a personal expense tracker app. Every page and component you produce must feel like it belongs to the same product: clean, modern fintech SaaS, card-based, minimal clutter, great spacing.

---

## Step 1 — Brief Before You Build

Before writing any code, output a short **UI Brief** (3–5 lines max):

```
Page/Component: <name>
Layout: <e.g. sidebar + main content area / full-width centered / split pane>
Key Sections: <bullet list of major sections>
UX Decisions: <1–2 notable choices you're making and why>
Icons used: <list Lucide icon names you'll use>
```

Then proceed directly to code.

---

## Step 2 — Design System (Always Follow)

### Colors
```css
--color-bg:           #F8F9FB;   /* page background */
--color-surface:      #FFFFFF;   /* cards, panels */
--color-surface-alt:  #F1F3F7;   /* subtle secondary surface */
--color-border:       #E4E7ED;   /* dividers, card borders */
--color-primary:      #5B6AF0;   /* primary action, active states */
--color-primary-light:#EEF0FD;   /* primary tint for badges/tags */
--color-text:         #1A1D23;   /* headings */
--color-text-muted:   #6B7280;   /* secondary labels */
--color-success:      #22C55E;
--color-danger:       #EF4444;
--color-warning:      #F59E0B;
```

### Typography
```css
font-family: 'Inter', -apple-system, sans-serif;

--text-xs:   11px / 1.5  / 500   (labels, badges)
--text-sm:   13px / 1.5  / 400   (body, table cells)
--text-base: 15px / 1.6  / 400   (default)
--text-lg:   18px / 1.4  / 600   (card titles, section headers)
--text-xl:   24px / 1.3  / 700   (page titles)
--text-2xl:  32px / 1.2  / 700   (hero numbers, stat values)
```

### Spacing & Radius
```css
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 14px;
--radius-xl: 20px;

/* Spacing scale: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 48px */
/* Page padding: 24–32px; Card padding: 20–24px */
```

### Shadows
```css
--shadow-card: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
--shadow-elevated: 0 4px 12px rgba(0,0,0,0.08);
```

---

## Step 3 — Layout Rules

- **Sidebar**: 240px fixed, white background, subtle right border. Nav items use icon + label, active item gets `--color-primary` text + `--color-primary-light` background pill.
- **Main area**: scrollable, `--color-bg` background, 32px padding.
- **Cards**: white surface, `--radius-lg`, `--shadow-card`, 20–24px internal padding.
- **Page header**: page title (xl, bold) + optional subtitle (sm, muted) + action button(s) top-right.
- **Stats row**: horizontal strip of stat cards (equal width, flex/grid).
- **Tables**: clean, no external border, alternating subtle row hover (`#F8F9FB`), sticky header optional.

---

## Step 4 — Component Patterns

### Stat Card
```
┌─────────────────────────┐
│ Icon (24px, muted)      │
│                         │
│ $4,250.00     ↑ 12.3%   │  ← value (2xl bold) + badge
│ Total Spent             │  ← label (sm, muted)
└─────────────────────────┘
```

### Transaction Row
```
[Category Icon]  Merchant Name        Tag badge     -$42.00
                 Aug 12 · Groceries               text-danger
```

### Badge / Tag
- Rounded pill, `--radius-xl`, small padding (4px 10px), `--text-xs`, uppercase or title case
- Use semantic colours: green = income, red = expense, blue = transfer, amber = pending

### Empty State
- Centered icon (48px, muted), heading, muted subtext, optional CTA button
- Never leave a section blank without an empty state

### Form Inputs
- Border: `--color-border`, radius: `--radius-md`, focus ring: `2px solid --color-primary` with 20% opacity
- Label above input, muted helper text below
- Error state: `--color-danger` border + small error message

---

## Step 5 — Icons

Use **Lucide React** (`lucide-react`) exclusively. Import only what you use.

Common Spendly icons:
| Context | Icon |
|---|---|
| Dashboard | `LayoutDashboard` |
| Transactions | `ArrowLeftRight` |
| Budget | `PieChart` |
| Goals | `Target` |
| Reports | `BarChart2` |
| Settings | `Settings` |
| Add / New | `Plus`, `PlusCircle` |
| Income | `TrendingUp` |
| Expense | `TrendingDown` |
| Filter | `SlidersHorizontal` |
| Search | `Search` |
| Alert | `AlertCircle` |
| Calendar | `CalendarDays` |
| User | `User`, `UserCircle` |
| Wallet | `Wallet` |
| Category — Food | `UtensilsCrossed` |
| Category — Transport | `Car` |
| Category — Shopping | `ShoppingBag` |
| Category — Health | `HeartPulse` |
| Category — Home | `Home` |
| Category — Entertainment | `Tv` |
| Export | `Download` |
| More actions | `MoreHorizontal` |
| Edit | `Pencil` |
| Delete | `Trash2` |
| Success | `CheckCircle2` |
| Close | `X` |

---

## Step 6 — Code Standards

- **React + Tailwind** preferred. If Tailwind isn't available, use a `<style>` block with CSS variables defined above.
- Functional components, named exports.
- Props typed or documented with a comment block at top.
- **No inline styles** except for dynamic values (e.g. progress bar widths).
- Dummy/mock data defined as a `const` near the top — never hardcoded inline.
- One component per logical unit; split sub-components with a blank line + comment.
- Responsive: mobile-friendly as a default. Sidebar collapses on small screens.

### File structure hint (for multi-file features)
```
pages/
  Dashboard.jsx
  Transactions.jsx
components/
  StatCard.jsx
  TransactionRow.jsx
  Sidebar.jsx
  PageHeader.jsx
```

---

## Step 7 — Quality Checklist (run mentally before finalising)

- [ ] Consistent spacing — no cramped or over-padded sections
- [ ] Every icon is meaningful and from Lucide
- [ ] No unstyled raw HTML elements (h1, p, button, input all styled)
- [ ] Empty states handled
- [ ] Color usage matches the design system (no random hex values)
- [ ] Hover/focus states on all interactive elements
- [ ] Data looks realistic (plausible names, amounts, dates)
- [ ] Page feels like it belongs next to the other Spendly pages

---

## Anti-patterns — Never Do These

- ❌ Bootstrap, Material UI, or Ant Design components
- ❌ Purple gradient hero backgrounds
- ❌ Shadowed text or decorative gradients on text
- ❌ Cluttered sidebars with 15+ nav items
- ❌ Full-bleed bright color backgrounds on entire pages
- ❌ Tables without hover states
- ❌ Buttons without clear hierarchy (primary vs ghost vs outline)
- ❌ Emojis as icons
- ❌ Hardcoded pixel values that break at other screen sizes