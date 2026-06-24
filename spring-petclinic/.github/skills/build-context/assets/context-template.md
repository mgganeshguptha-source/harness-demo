# context.md Template — All Story Types & Development Layers

---

## Universal Sections (All Story Types, All Layers)

### Section 1 — What Are We Trying to Achieve
**Required:** Always
**Purpose:** One paragraph — the goal in plain language

| Story Type | Focus |
|---|---|
| Bug Fix | What is broken and why fixing it matters |
| New Dev | The user goal and business value |
| Enhancement | What limitation is being addressed |

---

### Section 2 — Current Behaviour
**Required:** Bug Fix and Enhancement only. Skip for New Dev if nothing exists.

**Backend:** `GET /api/v1/owners?lastName=Smith returns all owners regardless of parameter`
**Frontend:** `Appointment form submits without validating the date field — past dates accepted`
**Full Stack:** `Search screen shows all owners on load. API ignores query parameter.`

---

### Section 3 — Expected Behaviour
**Required:** Always — always verify, most commonly vague

**Backend:** `Returns only owners whose lastName contains "Smith" (case-insensitive, partial match). Paginated, default 20.`
**Frontend:** `Past date entry shows inline error below field. Form does not submit. Field highlighted red.`
**Full Stack:** `User types in search box → API filters results → list updates → loading spinner during call → empty state if no results`

---

### Section 4 — Acceptance Criteria
**Required:** Always — minimum 2, ideally 3+. Each must be independently testable.

**Backend:** `AC1: Filtered results contain only matching owners | AC2: Case-insensitive | AC3: Empty param returns all owners`
**Frontend:** `AC1: Error shown on invalid date | AC2: Error clears on valid selection | AC3: Form blocked while error visible`
**Full Stack:** `AC1: Results filter on API and UI | AC2: Loading spinner visible | AC3: Empty state shown | AC4: Works on mobile`

---

### Section 5 — Edge Cases
**Required:** Always

**Backend:** `null param, empty string, special chars (O'Brien), very long input, injection attempts`
**Frontend:** `Keyboard submit, screen reader announcement, slow network double-click, mobile keyboard overlap`
**Full Stack:** `Network failure, API 500 error, search during previous search in progress, session expiry`

---

### Section 6 — Constraints
**Required:** Always — auto-filled from copilot-instructions.md

**Backend (auto):** `Constructor injection | Standard error format | Jakarta Validation | JUnit 5 + Mockito | Pagination`
**Frontend (auto):** `Existing component library | Keyboard navigation | ARIA labels | Responsive 375px-1440px | Component tests`
**Full Stack:** Both sets above plus `API contract must not break existing consumers`

---

### Section 7 — Out of Scope
**Required:** Always — prevents Copilot over-engineering

**Backend:** `firstName search | sorting | performance optimisation | email notification`
**Frontend:** `Full redesign | time zones | cancellation flow`
**Full Stack:** `Advanced filters | export | search history | URL update on search`

---

### Section 8 — Clarifications Needed
**Required:** Only if genuine ambiguities exist

**Backend:** `[NEEDS CLARIFICATION]: Partial or exact match? | Maximum page size?`
**Frontend:** `[NEEDS CLARIFICATION]: Error on blur or submit? | Design for error state available?`
**Full Stack:** `[NEEDS CLARIFICATION]: Search on keypress or button? | Min characters before search fires?`

---

## Complete Examples

### Backend Bug Fix
```markdown
## What Are We Trying to Achieve
Fix the owner search API which ignores the lastName parameter
and returns all owners, preventing clinic staff from finding
specific owners efficiently.

## Current Behaviour
GET /api/v1/owners?lastName=Smith returns all owners regardless
of the lastName parameter value.

## Expected Behaviour
Returns only owners whose lastName contains "Smith"
(case-insensitive, partial match). Results paginated, default 20.

## Acceptance Criteria
- AC1: Filtered results contain only matching owners
- AC2: Search is case-insensitive
- AC3: Empty lastName returns all owners with 200
- AC4: No results returns 200 with empty array, not 404
- AC5: Results are paginated

## Edge Cases
- null parameter: return all owners
- Special characters (O'Brien, García): handled correctly
- Very long input: return 400 validation error

## Constraints
- Constructor injection throughout
- Standard error response format
- Jakarta Validation on parameters
- JUnit 5 + Mockito tests
- Pagination for results

## Out of Scope
- firstName search not in this story
- Sorting of results not in scope

## Clarifications Needed
- [NEEDS CLARIFICATION]: Partial match or exact match only?
```

---

### Frontend New Development
```markdown
## What Are We Trying to Achieve
Build a new appointment booking form so pet owners can
schedule visits directly from the portal without calling.

## Current Behaviour
No booking form exists — owners call the clinic to book.

## Expected Behaviour
Form with: pet selection dropdown, vet dropdown, future-only
date picker, reason text area. On submit: confirmation message.

## Acceptance Criteria
- AC1: All fields required — form blocked if any empty
- AC2: Date picker only allows future dates
- AC3: Pet dropdown shows only logged-in owner's pets
- AC4: Success message shown after booking confirmed
- AC5: Works on mobile (375px) and desktop (1440px)

## Edge Cases
- No pets registered: show "Please add a pet first"
- No vets available: show availability message
- Network failure on submit: show error, keep form data
- Double submit: only one request sent

## Constraints
- Follow existing design system components
- Keyboard navigation for all fields
- ARIA labels on all inputs and errors
- Responsive layout
- Component unit tests

## Out of Scope
- Payment processing not in scope
- Appointment cancellation not in scope
- Email confirmation not in scope

## Clarifications Needed
- [NEEDS CLARIFICATION]: Can owners book for multiple pets in one form?
- [NEEDS CLARIFICATION]: How far ahead can appointments be booked?
```

---

### Full Stack Enhancement
```markdown
## What Are We Trying to Achieve
Enhance owner search so results update live as the user types,
removing the need to click Search and speeding up busy workflows.

## Current Behaviour
Owner search requires typing lastName and clicking Search.
API correctly filters by lastName. Results replace full list on click.

## Expected Behaviour
After 3 characters typed, results update automatically with 300ms
debounce. Loading spinner shown. Empty state if no results.
Search button remains for accessibility.

## Acceptance Criteria
- AC1: Results update after 3 characters without clicking Search
- AC2: 300ms debounce — API not called on every keystroke
- AC3: Loading spinner visible during API call
- AC4: Empty state "No owners found" when no results
- AC5: Search button still works for keyboard/screen reader users
- AC6: Clearing search restores full owner list

## Edge Cases
- Slow network: previous results stay until new ones arrive
- User types faster than debounce: only last query fires
- Network failure: show "Something went wrong, try again"
- Screen reader: result count announced after update

## Constraints
- API contract unchanged — existing consumers not affected
- Constructor injection throughout backend
- Standard error response format
- 300ms debounce on frontend
- ARIA live region for result updates
- Unit tests for debounce behaviour

## Out of Scope
- Advanced filters not in scope
- Search history not in scope
- URL update on search not in scope

## Clarifications Needed
- [NEEDS CLARIFICATION]: 2 or 3 minimum characters before search?
- [NEEDS CLARIFICATION]: Same live search on mobile or button-click?
```
