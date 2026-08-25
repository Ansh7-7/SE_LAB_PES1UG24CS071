# SE Lab 1 — Requirements Engineering & UML Use-Case Modelling

**Problem Statement #36 — Restaurant Table Booking & Pre-Ordering App**
A hospitality app that lets diners pick a table on a live 2D floor plan, place advance
food orders, and get a kitchen prep timeline for seamless arrival dining.

**Actors:** Diner, Restaurant Manager, Payment Gateway (external), Kitchen Display System (external)

## Deliverables in this folder

| File | Deliverable |
|------|-------------|
| `Requirements_Table.xlsx` | 5 FRs (FR-001…FR-005) + 2 NFRs (NFR-001, NFR-002) with ID, Type, Description, Priority, Acceptance Criteria, Rationale |
| `UseCase_Diagram.pdf` | UML use-case diagram — actors, 8 use cases, 3 «include» + 1 «extend» |
| `UseCase_Flow.docx` / `UseCase_Flow.pdf` | One-page flow for UC-03 (Book Table & Pre-Order): Preconditions, Postconditions, Main Success Scenario, Alternate Flows |

## Repository setup (per lab instructions)

```
SE-Labs-<SRN>/          # public repo under your GitHub account
└── Lab1/               # this directory
    ├── Requirements_Table.xlsx
    ├── UseCase_Diagram.pdf
    ├── UseCase_Flow.docx
    ├── UseCase_Flow.pdf
    └── README.md
```

```bash
git init
git add Lab1/
git commit -m "Lab 1: PS#36 Restaurant Table Booking & Pre-Ordering App"
git branch -M main
git remote add origin https://github.com/<username>/SE-Labs-<SRN>.git
git push -u origin main
```
