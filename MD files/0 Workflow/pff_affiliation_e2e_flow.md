# PFF Affiliation — Complete E2E Flow (All Scenarios)
> Generated: 2026-08-07 | PFF / The FA

---

## PHASE 0 — PRE-AFFILIATION SETUP (County Portal — CFA Admin)

```
CFA Admin sets up in County Portal BEFORE affiliation window opens:
┌─────────────────────────────────────────────────────────────────────┐
│  PRODUCTS SETUP (County Portal > Products Tab)                      │
│                                                                     │
│  A. Team Fee Products (Affiliation Tab)                             │
│     • Set per team category (Adult, Youth, Pro Game, etc.)          │
│     • Mapped to age group, format, football level, disability       │
│     • Can be set to £0 if required                                  │
│     • Calculated Products: Club Fee (highest tier) + Team Fees      │
│                                                                     │
│  B. Club Insurance Products (Affiliation Tab > Insurance)           │
│     • Public Liability (PL) Insurance — covers whole club           │
│       - CFA sets up group cover (e.g. via Bluefin)                  │
│       - OR club uploads own policy document                         │
│     • Personal Accident (PA) Insurance — covers each team           │
│       - CFA sets up group cover for clubs to opt into               │
│       - OR club purchases own / uploads own policy                  │
│     • Multiple levels of cover available (6-8 tiers)                │
│     • Mandatory or Optional per CFA configuration                   │
│                                                                     │
│  C. Other Products (Optional)                                       │
│     • Handbooks, equipment, badges, county-specific products        │
│     • Set as Mandatory / Additional / Optional                      │
│                                                                     │
│  D. County Cup Products                                             │
│     • Entry criteria set (age group, gender, step level, day)       │
│     • Eligibility rules configured per cup                          │
│                                                                     │
│  E. Affiliation Window Dates                                        │
│     • County-wide open/close dates configured                       │
│     • Early access dates for specific clubs (if needed)             │
│     • isCfaReviewRequired flag set per county/club type             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1 — CLUB CHECKS (Club Portal — Club Admin)

```
Club Admin navigates to Teams Tab → clicks "Affiliate Team"
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SYSTEM RUNS CLUB CHECKS                                            │
│                                                                     │
│  ✔ Mandatory Club Officials assigned                                │
│  ✔ Mandatory Team Officials assigned                                │
│  ✔ Officials have valid Safeguarding / DBS                          │
│    (Youth teams U5-U18: Manager/Coach + CRC mandatory)              │
│    (CFA can allow "CRC In Progress" override)                       │
│  ✔ Officials not suspended (CFA can override "Accept Suspended")    │
│  ✔ Ground assigned to team                                          │
│  ✔ League membership assigned                                       │
│  ✔ No Overdue Debt (PFF Debt Logic — PF-58434)                      │
│    Debt = any unpaid invoice past due date:                         │
│    - Affiliation invoices (overdue after 14 days)                   │
│    - County Cup invoices (overdue after 14 days)                    │
│    - Discipline/GRF cases (overdue after 14 days + next Tuesday)    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
   ALL CHECKS PASS ✅               ONE OR MORE CHECKS FAIL ❌
          │                                 │
          │                                 ▼
          │                    ╔════════════════════════════════╗
          │                    ║ SCENARIO 1                     ║
          │                    ║ PRE-CHECK FAILURE              ║
          │                    ║ App NOT created                ║
          │                    ║ Banner shown to Club Admin:    ║
          │                    ║ "Fix officials / safeguarding  ║
          │                    ║  / insurance / ground /        ║
          │                    ║  league / debt before          ║
          │                    ║  proceeding"                   ║
          │                    ║ Club must resolve & retry      ║
          │                    ╚════════════════════════════════╝
          │
          ▼
  Application Created → STATUS: IN PROGRESS
```

---

## PHASE 2 — SELECT TEAMS & ASSIGN TEAM FEE PRODUCTS

```
Club Admin selects teams to affiliate
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SELECT TEAMS STEP                                                  │
│  • Only eligible (non-folded, non-affiliated) teams shown           │
│  • Club Admin selects one or more teams                             │
│  • System auto-assigns Team Fee Product per team                    │
│    based on: age group + format + football level + disability       │
│    e.g. "Adult - Open Aged - Club Fee" = £X                         │
│  • Total fee = Highest Club Fee + sum of all Team Fees              │
│                                                                     │
│  SCENARIO 2A: FOLDED TEAM SUBMISSION ATTEMPT                        │
│  • Club tries to include a folded team                              │
│  • System blocks submission (PF-25182 fix)                          │
│  • Club must unfold team first (within 14-day cooling period)       │
│    or select different teams                                        │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
```

---

## PHASE 3 — INSURANCE STEP (All Scenarios)

```
┌─────────────────────────────────────────────────────────────────────┐
│  INSURANCE STEP — Club Admin selects insurance for club & teams     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         ▼                                    ▼
  CLUB INSURANCE (PL)                  TEAM INSURANCE (PA)
  Public Liability — covers club        Personal Accident — per team
         │                                    │
    ┌────┴────┐                          ┌────┴────┐
    ▼         ▼                          ▼         ▼
SCENARIO 3A  SCENARIO 3B           SCENARIO 3C  SCENARIO 3D
PURCHASE     UPLOAD OWN            PURCHASE     UPLOAD OWN
CFA GROUP    POLICY DOC            CFA GROUP    POLICY DOC
COVER        (PDF upload)          COVER        (PDF upload per team)
    │         │                        │         │
    │         ▼                        │         ▼
    │   Malware scan runs              │   Malware scan runs
    │   on uploaded doc                │   on uploaded doc
    │         │                        │         │
    └────┬────┘                        └────┬────┘
         ▼                                  ▼
  Club Insurance confirmed           Team Insurance confirmed
  (product or document stored)       (product or document stored)
         │                                  │
         └──────────────┬───────────────────┘
                        ▼
              SCENARIO 3E: ALREADY INSURED
              Club already has valid insurance
              from a previous completed application
              → System shows "Already Insured"
              → Club can proceed without re-purchasing
              → Load test shows "already club insured" path
                (PF-63783 / PF-65436)
```

---

## PHASE 4 — OTHER PRODUCTS STEP

```
┌─────────────────────────────────────────────────────────────────────┐
│  OTHER PRODUCTS STEP (Optional)                                     │
│  • CFA-configured optional/mandatory products shown                 │
│  • e.g. Handbooks, equipment, badges, county-specific items         │
│                                                                     │
│  SCENARIO 4A: NO OTHER PRODUCTS                                     │
│  • CFA has no other products configured → step skipped              │
│                                                                     │
│  SCENARIO 4B: MANDATORY OTHER PRODUCTS                              │
│  • Club must purchase before proceeding                             │
│                                                                     │
│  SCENARIO 4C: OPTIONAL OTHER PRODUCTS                               │
│  • Club can choose to purchase or skip                              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
```

---

## PHASE 5 — SUMMARY & SUBMISSION

```
┌─────────────────────────────────────────────────────────────────────┐
│  SUMMARY PAGE                                                       │
│  • Teams selected + Team Fee Products                               │
│  • Club Insurance (PL) — purchased or uploaded                      │
│  • Team Insurance (PA) — purchased or uploaded per team             │
│  • Other Products selected                                          │
│  • Total Fee displayed                                              │
│  • Submission details (name, email, role)                           │
│  • pendingReviewReasons evaluated:                                  │
│    - isOutstandingDebt                                              │
│    - isWelfareOfficerNonCompliance                                  │
│    - isDocumentUploaded                                             │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
              Club Admin clicks SUBMIT
                           │
                           ▼
         System re-validates all requirements
                           │
          ┌────────────────┴────────────────────────┐
          ▼                                         ▼
  isCfaReviewRequired = FALSE               isCfaReviewRequired = TRUE
  + No overdue debt                         OR overdue debt exists
  + No welfare officer non-compliance       OR welfare officer issue
  + No document uploaded flag               OR document uploaded flag
          │                                         │
          ▼                                         ▼
```

---

## PHASE 6 — APPLICATION ROUTING (All Approval Scenarios)

```
══════════════════════════════════════════════════════════════════════
SCENARIO 5: AUTO-APPROVE
══════════════════════════════════════════════════════════════════════
All checks pass, no CFA review required
STATUS → COMPLETE (immediately, no CFA involvement)
• Teams stamped AFFILIATED
• WGS integration triggered (see Phase 8)
• Team officials & league memberships activated
• Affiliation date stamped on each team
• Insurance documents stored in Club Portal > Policies & Plans tab
• 📧 "Affiliation Complete" email → Club Admin
  (includes: teams, fee, county name, application ID)

══════════════════════════════════════════════════════════════════════
PENDING CFA PATH
══════════════════════════════════════════════════════════════════════
STATUS → PENDING CFA
📧 "Application requires CFA review" → County Admin
CFA Admin reviews in County Portal:
  - Team details, safeguarding, finance, discipline history,
    competition entries, insurance documents

         │
         ├──────────────────────────────────────────────────────────┐
         │  CFA APPROVES (fee > £0)                                 │
         │                                                          │
         │  SCENARIO 6: CFA APPROVES → INVOICED                    │
         │  STATUS → INVOICED (Awaiting Payment)                    │
         │  • Invoice created in PAAS / Payment Service             │
         │  • Invoice number mapped to application                  │
         │  • Fee = Team Fees + Club Fee + Insurance + Other Prods  │
         │  • 📧 "Awaiting Payment" → Club Admin                    │
         │    (includes: invoice number, old/new fee, removed teams)│
         │                                                          │
         │  Club Admin pays via Club Portal > Payments Tab          │
         │         │                                                │
         │    ┌────┴────┐                                           │
         │    ▼         ▼                                           │
         │  ONLINE    OFFLINE                                       │
         │  PAYMENT   PAYMENT                                       │
         │    │         │                                           │
         │    ▼         ▼                                           │
         │  SCENARIO 7  SCENARIO 8                                  │
         │  ONLINE PAY  OFFLINE PAY                                 │
         │  (SmartPay   (CFA marks                                  │
         │   Fuse)       paid offline)                              │
         │    │         │                                           │
         │    └────┬────┘                                           │
         │         ▼                                                │
         │  STATUS → COMPLETE                                       │
         │  • Payment confirmed                                     │
         │  • Invoice marked PAID in Xero                           │
         │  • Teams stamped AFFILIATED                              │
         │  • WGS integration triggered                             │
         │  • Insurance docs stored in Club Portal                  │
         │  • 📧 "Affiliation Complete" → Club Admin                │
         └──────────────────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────────────────────────┐
         │  CFA APPROVES (fee = £0)                                 │
         │                                                          │
         │  SCENARIO 9: CFA APPROVES £0 — NO PAYMENT               │
         │  STATUS → COMPLETE (directly, no payment step)           │
         │  • No invoice created                                    │
         │  • Teams stamped AFFILIATED                              │
         │  • WGS integration triggered                             │
         │  • 📧 "Affiliation Complete" → Club Admin                │
         └──────────────────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────────────────────────┐
         │  CFA REJECTS                                             │
         │                                                          │
         │  SCENARIO 10: CFA REJECTS                               │
         │  STATUS → REJECTED                                       │
         │  • Teams remain UNAFFILIATED                             │
         │  • 📧 "Affiliation Rejected" → Club Admin                │
         │    (includes: reason, county name, application ID)       │
         │  • Club can edit & resubmit new application              │
         └──────────────────────────────────────────────────────────┘
         │
         └──────────────────────────────────────────────────────────┐
            CFA CANCELS                                             │
                                                                    │
            SCENARIO 11: CFA CANCELS                               │
            STATUS → CANCELLED                                      │
            • Teams become UNAFFILIATED                             │
            • 📧 "Affiliation Cancelled" → Club Admin               │
              (includes: reason, county name, application ID)       │
            • Club can submit new application                       │
            └────────────────────────────────────────────────────────┘
```

---

## PHASE 7 — TIMER & SYSTEM-TRIGGERED SCENARIOS

```
══════════════════════════════════════════════════════════════════════
SCENARIO 12: AUTO-CANCEL (SEASON END TIMER)
══════════════════════════════════════════════════════════════════════
AffiliationApplicationCancelTimerTrigger
Fires: 1AM on 31st May (yearly)
Targets:
  • All IN PROGRESS applications from current season
  • All PENDING CFA applications from previous season
  • All INVOICED (Awaiting Payment) apps from previous season
STATUS → CANCELLED
• Teams remain UNAFFILIATED
• 📧 Notification → affected clubs
• (PF-61969 — fix for timer not running in QA)

══════════════════════════════════════════════════════════════════════
SCENARIO 13: SEASON ROLLOVER (June 1st PFF / July 1st WGS)
══════════════════════════════════════════════════════════════════════
• PFF rolls over to new season on June 1st
• Teams from previous season carried forward (projected)
  - U17+ teams replicated as-is
  - U16 and below aged up one year
• Team officials moved with teams
• Default league entries assumed same
• Clubs must re-affiliate teams for new season
• WGS rolls over July 1st (1-month gap)
  - During gap: PFF = new season, WGS = old season
• Last season's data shown as static snapshot for 30 days
• TeamDeactivationTimerTrigger fires to deactivate old season teams

══════════════════════════════════════════════════════════════════════
SCENARIO 14: TEAM FOLD (during affiliation window)
══════════════════════════════════════════════════════════════════════
• Club folds a team that is IN an active application
• Folded team removed from application
• If application still has other teams → continues
• If no teams remain → application effectively empty
• TeamDeactivationTimerTrigger fires after 14-day cooling period
• Club can unfold within 14-day cooling period
• Insurance documents remain (may cover other teams)
• 📧 Fold notification → CFA Admin
```

---

## PHASE 8 — WGS INTEGRATION (on COMPLETE)

```
══════════════════════════════════════════════════════════════════════
SCENARIO 15: FIRST AFFILIATION IN SEASON
(No Club-Affiliation membership record exists in WGS)
══════════════════════════════════════════════════════════════════════
• Create new Club Affiliation membership in WGS for current season
• Generate affiliation number
• Make affiliated teams ACTIVE in WGS
• Activate team officials & league memberships for affiliated teams
• Stamp affiliation date against each team
• County cups / League cups activated

══════════════════════════════════════════════════════════════════════
SCENARIO 16: ADDITIONAL APPLICATION (same season)
(Club-Affiliation membership already exists in WGS)
══════════════════════════════════════════════════════════════════════
• Attach new teams to existing WGS Club-Affiliation membership
• Activate team officials & league memberships for new teams
• Stamp affiliation date against new teams
• No new affiliation number created

══════════════════════════════════════════════════════════════════════
SCENARIO 17: COMPLETED APPLICATION CANCELLED (post-complete)
══════════════════════════════════════════════════════════════════════
• WGS reversal: TBC (documented as TBC in source)
• Teams → UNAFFILIATED in PFF
• Invoice should be voided
• 📧 "Affiliation Cancelled" → Club Admin
```

---

## PHASE 9 — POST-COMPLETE SCENARIOS

```
══════════════════════════════════════════════════════════════════════
SCENARIO 18: REFUND (Partial or Full)
══════════════════════════════════════════════════════════════════════
Trigger: CFA/FA Admin applies credit note in Xero / SmartPayFuse
• Invoice status → Refunded
• 📧 "Payment Refund for Affiliation" → Club Admin
  (includes: invoice number, amount, refund date, county name)
• If CFA initiated → CFA also receives refund email
• If FA initiated → FA also receives refund email
• Team remains AFFILIATED (unless full cancel follows)
• Refund credited back to original payment card (3-5 days)

══════════════════════════════════════════════════════════════════════
SCENARIO 19: TEAM FOLD (post-affiliation)
══════════════════════════════════════════════════════════════════════
• Club folds team in Club Portal after affiliation is COMPLETE
• Team affiliation status → removed
• TeamDeactivationTimerTrigger fires after 14-day cooling period
• Insurance documents remain (may cover other teams in club)
• Club can unfold within 14-day cooling period
• 📧 Fold notification → CFA Admin

══════════════════════════════════════════════════════════════════════
SCENARIO 20: INSURANCE DOCUMENT MANAGEMENT (post-complete)
══════════════════════════════════════════════════════════════════════
• Insurance docs auto-allocated to Club Portal > Policies & Plans tab
  (PF-54040 — Automate Allocation of Insurance Documentation)
• Only displayed when linked application = COMPLETE
• Club Admin: can view + download (cannot delete non-expired docs)
• CFA/FA Admin: can view + download + delete at any time
• If affiliation application expires → doc shows "Expired" tag
  + delete enabled for Club Admin
• If team affiliation cancelled → insurance NOT auto-removed
  (may cover other teams — manual removal by CFA if needed)
```

---

## PHASE 10 — PAYMENT FAIL STATE SCENARIOS

```
══════════════════════════════════════════════════════════════════════
SCENARIO 21: INVOICE NOT CREATED IN PAAS
══════════════════════════════════════════════════════════════════════
• App = INVOICED but no invoice exists to pay
• Club Admin gets error when trying to pay
• Affiliation blocked
• Resolution: Grafana monitor → data fix or CFA cancel
• Likelihood: Very low (network glitch)

══════════════════════════════════════════════════════════════════════
SCENARIO 22: INVOICE CREATED BUT NOT MAPPED TO APP ID
══════════════════════════════════════════════════════════════════════
• App = INVOICED, invoice exists in PAAS
• Club Admin gets error when trying to pay
• Resolution: Data fix / repush message
• Likelihood: Very low (network glitch)

══════════════════════════════════════════════════════════════════════
SCENARIO 23: PAID OFFLINE BUT INVOICE STILL UNPAID IN XERO
══════════════════════════════════════════════════════════════════════
• Team = AFFILIATED, invoice = unpaid/overdue in Xero
• Impacts debt calculation for future affiliations
• Resolution: Manual reconciliation in Xero
• Risk: Club flagged as having overdue debt next season

══════════════════════════════════════════════════════════════════════
SCENARIO 24: APP CANCELLED BUT INVOICE NOT VOIDED
══════════════════════════════════════════════════════════════════════
• Team = UNAFFILIATED, invoice still shows as active
• Impacts debt calculation
• Resolution: Void invoice in Xero manually

══════════════════════════════════════════════════════════════════════
SCENARIO 25: INVOICE NOT POSTED TO XERO
══════════════════════════════════════════════════════════════════════
• Club CAN pay & complete affiliation
• But payment won't reconcile in Xero
• Download invoice disabled for users
• Resolution: Confirm with Blue Hub / Xero API

══════════════════════════════════════════════════════════════════════
SCENARIO 26: 500 ERROR ON SUBMISSION (club insurance product issue)
══════════════════════════════════════════════════════════════════════
• Club submits application → receives 500 error
• BUT team affiliation status changes to "Pending CFA"
• CFA portal shows pending application but club insurance
  product not found → team cannot be affiliated
• (PF-50604 — known bug)
• Resolution: Data fix / CFA cancel and resubmit

══════════════════════════════════════════════════════════════════════
SCENARIO 27: PRODUCT VALIDATION 404 ERROR
══════════════════════════════════════════════════════════════════════
• Other Product Validation API returns 404
• Club gets 500 error on submission
• Workaround implemented (PF-64286)
• Permanent fix in progress
```

---

## PHASE 11 — EDGE CASE SCENARIOS

```
══════════════════════════════════════════════════════════════════════
SCENARIO 28: SUSPENDED OFFICIAL ON APPLICATION
══════════════════════════════════════════════════════════════════════
• Club submits with an official who has a current suspension
• System alerts CFA on review
• CFA checks if suspension prevents the official role
• If not blocking → CFA checks "Accept Suspended Officials"
• Application can proceed

══════════════════════════════════════════════════════════════════════
SCENARIO 29: YOUTH TEAM — CRC IN PROGRESS
══════════════════════════════════════════════════════════════════════
• Youth team (U5-U18) has officials with CRC check in progress
  (status: Submitted to DBS / DBS Acknowledged / Disclosure Complete)
• Club can submit without completed CRC
• CFA can check "Allow CRC In Progress" to approve
• Application proceeds with CRC caveat

══════════════════════════════════════════════════════════════════════
SCENARIO 30: CLUB AFFILIATION CHANGE (mid-season)
══════════════════════════════════════════════════════════════════════
• Club changes affiliation (e.g. Sheffield United Women FC)
• Historical disciplinary data (Cases, Suspensions, Invoices)
  remains linked to old club ID
• Migration required to new club ID
• (REG-2023 / REG-2040)

══════════════════════════════════════════════════════════════════════
SCENARIO 31: DESELECTED TEAMS STILL SHOWING IN INSURANCE STEP
══════════════════════════════════════════════════════════════════════
• Club deselects teams on "Select Teams" screen
• Deselected teams still appear on Team Insurance screen
• (PF-51472 — known bug)
• Workaround: Club ignores deselected teams on insurance screen

══════════════════════════════════════════════════════════════════════
SCENARIO 32: INSURANCE DOCUMENT DELETION DURING PENDING CFA
══════════════════════════════════════════════════════════════════════
• Insurance documents uploaded in PENDING CFA applications
  were deletable (security issue)
• (PF-25073 — fixed in County Portal 5.5.0)
• Now: insurance docs in pending CFA apps are NOT deletable
```

---

## Complete Scenario Summary Table

| #    | Scenario                                          | Phase           | Final Status                  | Teams Affiliated?   |
|------|---------------------------------------------------|-----------------|-------------------------------|---------------------|
| 1    | Pre-check failure                                 | Club Checks     | No app created                | ❌                  |
| 2A   | Folded team submission attempt                    | Select Teams    | Blocked                       | ❌                  |
| 3A   | Purchase CFA group PL insurance                   | Insurance       | In Progress                   | ⏳                  |
| 3B   | Upload own PL insurance doc                       | Insurance       | In Progress                   | ⏳                  |
| 3C   | Purchase CFA group PA insurance                   | Insurance       | In Progress                   | ⏳                  |
| 3D   | Upload own PA insurance doc per team              | Insurance       | In Progress                   | ⏳                  |
| 3E   | Already insured (prior completed app)             | Insurance       | In Progress                   | ⏳                  |
| 4A   | No other products (step skipped)                  | Other Products  | In Progress                   | ⏳                  |
| 4B   | Mandatory other products purchased                | Other Products  | In Progress                   | ⏳                  |
| 4C   | Optional other products (skip or buy)             | Other Products  | In Progress                   | ⏳                  |
| 5    | Auto-approve (all checks pass)                    | Submission      | COMPLETE                      | ✅                  |
| 6    | CFA approves with fee → Invoiced                  | CFA Review      | INVOICED                      | ⏳                  |
| 7    | Club pays online (SmartPayFuse)                   | Payment         | COMPLETE                      | ✅                  |
| 8    | CFA marks paid offline                            | Payment         | COMPLETE                      | ✅                  |
| 9    | CFA approves £0 (no fee)                          | CFA Review      | COMPLETE                      | ✅                  |
| 10   | CFA rejects                                       | CFA Review      | REJECTED                      | ❌                  |
| 11   | CFA cancels                                       | CFA Review      | CANCELLED                     | ❌                  |
| 12   | Auto-cancel (timer, 31st May)                     | Timer           | CANCELLED                     | ❌                  |
| 13   | Season rollover (June 1st)                        | System          | Re-affiliate needed           | ❌                  |
| 14   | Team fold during affiliation                      | In Progress     | Team removed                  | ❌                  |
| 15   | WGS: First affiliation in season                  | Post-Complete   | COMPLETE + new WGS            | ✅                  |
| 16   | WGS: Additional app same season                   | Post-Complete   | COMPLETE + existing WGS       | ✅                  |
| 17   | Completed app cancelled (post-complete)           | Post-Complete   | CANCELLED                     | ❌                  |
| 18   | Refund (partial or full)                          | Post-Complete   | Refund processed              | ✅                  |
| 19   | Team fold post-affiliation                        | Post-Complete   | Team removed                  | ❌ (that team)      |
| 20   | Insurance doc management                          | Post-Complete   | Docs in Policies tab          | ✅                  |
| 21   | Invoice not created in PAAS                       | Payment Fail    | Blocked                       | ❌                  |
| 22   | Invoice created but not mapped to App ID          | Payment Fail    | Error on payment              | ❌                  |
| 23   | Paid offline but invoice still unpaid in Xero     | Payment Fail    | COMPLETE (reconcile risk)     | ✅ (risk)           |
| 24   | App cancelled but invoice not voided              | Payment Fail    | CANCELLED (invoice risk)      | ❌                  |
| 25   | Invoice not posted to Xero                        | Payment Fail    | COMPLETE (no reconciliation)  | ✅ (risk)           |
| 26   | 500 error on submission (insurance product)       | Payment Fail    | Error / Pending CFA           | ❌                  |
| 27   | Product validation 404 error                      | Payment Fail    | Error on submit               | ❌                  |
| 28   | Suspended official on application                 | CFA Review      | CFA override needed           | Conditional         |
| 29   | Youth team CRC in progress                        | CFA Review      | CFA override needed           | Conditional         |
| 30   | Club affiliation change mid-season                | Post-Complete   | Migration needed              | ✅ (new club)       |
| 31   | Deselected teams in insurance step                | Insurance       | Bug (known)                   | ⏳                  |
| 32   | Insurance doc deletion in Pending CFA             | CFA Review      | Fixed (PF-25073)              | ⏳                  |

---

## Application Status Reference

| Status              | Meaning                                                        |
|---------------------|----------------------------------------------------------------|
| IN PROGRESS         | Application created, club filling in details                   |
| PENDING CFA         | Submitted, awaiting CFA review                                 |
| INVOICED            | CFA approved with fee, club needs to pay                       |
| COMPLETE            | Affiliated — via auto-approve, £0 approval, or payment received|
| REJECTED            | CFA rejected — club can resubmit                               |
| CANCELLED           | CFA cancelled or auto-cancelled by timer                       |

---

## Notification Summary

| Trigger                          | Email                          | Recipient              |
|----------------------------------|--------------------------------|------------------------|
| Application requires CFA review  | CFA Review Required            | County Admin           |
| CFA approves with fee            | Awaiting Payment               | Club Admin             |
| CFA rejects                      | Affiliation Rejected           | Club Admin             |
| CFA cancels                      | Affiliation Cancelled          | Club Admin             |
| Application complete             | Affiliation Complete           | Club Admin             |
| Refund processed (CFA initiated) | Payment Refund                 | Club Admin + CFA Admin |
| Refund processed (FA initiated)  | Payment Refund                 | Club Admin + FA Admin  |
| Team fold                        | Team Fold Notification         | CFA Admin              |

---

## Key Decision Flags

| Flag                          | Effect                                                        |
|-------------------------------|---------------------------------------------------------------|
| isCfaReviewRequired = true    | Forces application to PENDING CFA                             |
| isOutstandingDebt = true      | Forces application to PENDING CFA                             |
| isWelfareOfficerNonCompliance | Forces application to PENDING CFA                             |
| isDocumentUploaded            | Forces application to PENDING CFA                             |
| Allow CRC In Progress         | CFA override — allows youth teams with pending DBS to proceed |
| Accept Suspended Officials    | CFA override — allows suspended officials on application      |

---

## Sources

- Affiliation page: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/5645271070/Affiliation+.
- WGS Integration: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/3622928400/Affiliation+Status+WGS+Integration
- Payments Fail States: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/3623059477/Payments+Fail+States
- Background Jobs: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/3764191238/PFF+Background+Jobs
- Master Club Debt: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/5653856275/Master+Club+Debt+in+PFF+-+Technical+Options
- Affiliation Email Templates: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/6096060444/Affiliation+Transactional+Email+templates
- Season Rollover 24/25: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/3855712273/PFF+Season+Rollover+2024-25
- Automate Insurance Allocation: https://the-fa.atlassian.net/browse/PF-54040
- PF-50604: https://the-fa.atlassian.net/browse/PF-50604
- PF-51472: https://the-fa.atlassian.net/browse/PF-51472
- PF-25073: https://the-fa.atlassian.net/browse/PF-25073
- PF-64286: https://the-fa.atlassian.net/browse/PF-64286
- PF-25182: https://the-fa.atlassian.net/browse/PF-25182
- PF-61969: https://the-fa.atlassian.net/browse/PF-61969
- County Portal 5.5.0: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/6120538160/PFF+County+Portal+5.5.0
- Epics & Documentation: https://the-fa.atlassian.net/wiki/spaces/SFF/pages/3622731787/Epics+Documentation
