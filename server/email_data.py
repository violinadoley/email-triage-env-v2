"""
Hardcoded email datasets for all three tasks.
All data is self-contained — no external files or network calls needed.
"""

from typing import Any, Dict, List

# ─── Task 1: classify_email ───────────────────────────────────────────────────
# Each entry: {"email": {...}, "label": str}

CLASSIFY_EMAILS: List[Dict[str, Any]] = [
    {
        "email": {
            "subject": "Congratulations! You've won $1,000,000!",
            "body": (
                "Dear Lucky Winner,\n\nYou have been selected as the grand prize winner "
                "of our international lottery. To claim your prize, please send your bank "
                "details and a processing fee of $500 to the address below.\n\n"
                "Click here: http://scam-lottery.xyz/claim"
            ),
            "sender": "noreply@lottery-winner.xyz",
            "timestamp": "2024-01-15T10:30:00Z",
        },
        "label": "spam",
    },
    {
        "email": {
            "subject": "Q3 Budget Review — Action Required",
            "body": (
                "Hi team,\n\nPlease review the attached Q3 budget spreadsheet and send your "
                "department's updated forecast by end of day Friday. The CFO needs consolidated "
                "numbers for the board meeting on Monday.\n\nThanks,\nSarah (Finance)"
            ),
            "sender": "sarah.johnson@acme-corp.com",
            "timestamp": "2024-01-15T09:00:00Z",
        },
        "label": "work",
    },
    {
        "email": {
            "subject": "Happy Birthday! 🎂",
            "body": (
                "Hey! Just wanted to wish you a wonderful birthday. "
                "Hope you have an amazing day filled with joy. "
                "Let's catch up soon — it's been too long!\n\nWith love, Maya"
            ),
            "sender": "maya.sharma@gmail.com",
            "timestamp": "2024-01-20T08:15:00Z",
        },
        "label": "personal",
    },
    {
        "email": {
            "subject": "This Week in AI: GPT-5 Rumors, Open-Source Models & More",
            "body": (
                "Welcome to this week's AI digest!\n\n"
                "• OpenAI reportedly testing GPT-5 internally\n"
                "• Mistral releases new open-weight model\n"
                "• Meta's LLaMA 4 benchmarks leaked\n\n"
                "Click to read the full stories. Unsubscribe | View in browser"
            ),
            "sender": "digest@ai-weekly.substack.com",
            "timestamp": "2024-01-21T07:00:00Z",
        },
        "label": "newsletter",
    },
    {
        "email": {
            "subject": "URGENT: Verify your account NOW or it will be suspended",
            "body": (
                "Your account has been compromised. Click the link below immediately to "
                "verify your identity and prevent suspension. Failure to act within 24 hours "
                "will result in permanent account deletion.\n\n"
                "Verify now: http://secure-account-verify.ru/login"
            ),
            "sender": "security@account-alerts.ru",
            "timestamp": "2024-01-16T14:22:00Z",
        },
        "label": "spam",
    },
    {
        "email": {
            "subject": "Code Review Request: PR #847 — Auth Refactor",
            "body": (
                "Hi,\n\nCould you take a look at PR #847 when you get a chance? "
                "I've refactored the authentication module to use JWT tokens instead of "
                "sessions. The change is non-breaking but I'd appreciate a second pair of eyes "
                "before merging.\n\nLink: github.com/acme/backend/pull/847\n\nThanks, Dev"
            ),
            "sender": "dev.patel@acme-corp.com",
            "timestamp": "2024-01-17T11:45:00Z",
        },
        "label": "work",
    },
    {
        "email": {
            "subject": "Re: Weekend plans?",
            "body": (
                "Hey! I'm free Saturday after 2 PM. "
                "Are you still up for hiking at Griffith Park? "
                "Let me know and I'll bring snacks!\n\nCheers, Raj"
            ),
            "sender": "raj.kumar@hotmail.com",
            "timestamp": "2024-01-18T18:30:00Z",
        },
        "label": "personal",
    },
    {
        "email": {
            "subject": "Your Monthly Product Updates — January 2024",
            "body": (
                "Hello,\n\nHere's what's new in your favorite tools this month:\n\n"
                "• Notion: New AI writing assistant\n"
                "• Figma: Variables now in beta\n"
                "• Linear: Roadmap view improvements\n\n"
                "Read the full changelog. Manage preferences | Unsubscribe"
            ),
            "sender": "updates@productboard.io",
            "timestamp": "2024-01-19T08:00:00Z",
        },
        "label": "newsletter",
    },
    {
        "email": {
            "subject": "Free iPhone 15 — Limited Time Offer!",
            "body": (
                "Congratulations! You've been pre-selected to receive a FREE iPhone 15 "
                "as part of our exclusive customer appreciation program. "
                "Just pay $9.99 shipping. Offer expires tonight!\n\n"
                "Claim your free phone: http://free-iphone-giveaway.net/claim"
            ),
            "sender": "offers@promo-deals.net",
            "timestamp": "2024-01-22T12:00:00Z",
        },
        "label": "spam",
    },
    {
        "email": {
            "subject": "Interview Feedback — Senior Engineer Role",
            "body": (
                "Hi,\n\nThank you for interviewing with us last week. "
                "We were impressed by your system design answers. "
                "After deliberation, we'd like to move you to the final round with our CTO. "
                "Please share your availability for next week.\n\nBest, HR Team at TechCorp"
            ),
            "sender": "recruiting@techcorp.com",
            "timestamp": "2024-01-23T10:00:00Z",
        },
        "label": "work",
    },
]


# ─── Task 2: prioritize_inbox (medium) ────────────────────────────────────────
# Each entry: {"emails": [...], "correct_ranking": [list of ids, most urgent first]}

PRIORITIZE_SCENARIOS: List[Dict[str, Any]] = [
    {
        "emails": [
            {
                "id": 1,
                "subject": "Production server DOWN — all services unreachable",
                "body": "CRITICAL: Our production environment is completely down. All customer-facing services are unreachable. Revenue impact: ~$10k/min. Need immediate response.",
                "sender": "ops-alerts@acme.com",
                "timestamp": "2024-01-15T09:05:00Z",
            },
            {
                "id": 2,
                "subject": "Board meeting slides due TODAY 3 PM",
                "body": "Reminder: The CEO needs the final Q4 slides by 3 PM today for the board presentation at 4 PM. Please finalize and send ASAP.",
                "sender": "ceo-assistant@acme.com",
                "timestamp": "2024-01-15T09:00:00Z",
            },
            {
                "id": 3,
                "subject": "Team lunch next Friday?",
                "body": "Hey! Thinking of organizing a team lunch next Friday at the Italian place. Are you in? Let me know by end of week.",
                "sender": "alice@acme.com",
                "timestamp": "2024-01-15T08:30:00Z",
            },
            {
                "id": 4,
                "subject": "Monthly newsletter — January edition",
                "body": "Here's the company newsletter for January. Highlights: new office in Austin, Q4 financials overview, upcoming events.",
                "sender": "newsletter@acme.com",
                "timestamp": "2024-01-15T08:00:00Z",
            },
            {
                "id": 5,
                "subject": "Contract renewal — please review before EOD",
                "body": "Attached is the vendor contract renewal for legal review. The current contract expires in 2 weeks. Please sign off before end of day.",
                "sender": "legal@acme.com",
                "timestamp": "2024-01-15T08:45:00Z",
            },
        ],
        "correct_ranking": [1, 2, 5, 3, 4],
    },
    {
        "emails": [
            {
                "id": 1,
                "subject": "Security breach detected — immediate action required",
                "body": "Our intrusion detection system has flagged unusual access to the customer database at 2:14 AM. Possible data exfiltration in progress. Escalating to incident response team.",
                "sender": "security@company.com",
                "timestamp": "2024-02-10T02:20:00Z",
            },
            {
                "id": 2,
                "subject": "Client call in 30 minutes — need the proposal",
                "body": "Hi, I have a call with Apex Corp in 30 minutes. They're expecting the final pricing proposal. Can you send it over right now? It should be in the shared drive.",
                "sender": "sales@company.com",
                "timestamp": "2024-02-10T09:30:00Z",
            },
            {
                "id": 3,
                "subject": "New blog post ideas — brainstorm?",
                "body": "Hey, I've been thinking about some new content directions for the company blog. Want to hop on a quick call this week to brainstorm?",
                "sender": "marketing@company.com",
                "timestamp": "2024-02-10T09:00:00Z",
            },
            {
                "id": 4,
                "subject": "Deploy to staging environment — approval needed",
                "body": "We have a critical bug fix ready. Need approval to deploy to staging for testing. The fix addresses a payment processing issue affecting ~15% of transactions.",
                "sender": "engineering@company.com",
                "timestamp": "2024-02-10T09:10:00Z",
            },
            {
                "id": 5,
                "subject": "Office supply order confirmation",
                "body": "Your order for pens, notebooks, and sticky notes has been confirmed. Expected delivery: 3-5 business days.",
                "sender": "supplies@officemax.com",
                "timestamp": "2024-02-10T08:55:00Z",
            },
        ],
        "correct_ranking": [1, 2, 4, 3, 5],
    },
    {
        "emails": [
            {
                "id": 1,
                "subject": "Apologies — missed your deadline",
                "body": "Hi, I'm so sorry I missed the deadline for the report you needed. I completely forgot. I'll have it done by tomorrow morning.",
                "sender": "colleague@company.com",
                "timestamp": "2024-03-05T16:00:00Z",
            },
            {
                "id": 2,
                "subject": "URGENT: Payroll processing error — 200 employees unpaid",
                "body": "Critical payroll issue: due to a system error, 200 employees did not receive their salary today. HR and Finance need to escalate immediately to fix this.",
                "sender": "hr@company.com",
                "timestamp": "2024-03-05T16:05:00Z",
            },
            {
                "id": 3,
                "subject": "Weekend team building activity — sign up!",
                "body": "We're planning a team building day next Saturday — escape room + lunch. Sign up by Friday if you're interested!",
                "sender": "hr-events@company.com",
                "timestamp": "2024-03-05T15:30:00Z",
            },
            {
                "id": 4,
                "subject": "Client escalation: service outage affecting enterprise account",
                "body": "Apex Corp (our largest enterprise customer) is experiencing a service outage. Their CTO is on the line. We need an engineer on the call immediately.",
                "sender": "support@company.com",
                "timestamp": "2024-03-05T16:02:00Z",
            },
            {
                "id": 5,
                "subject": "Article recommendation: Future of Remote Work",
                "body": "Thought you might find this interesting — HBR published a great piece on the future of hybrid work models. Sharing in case you missed it.",
                "sender": "colleague2@company.com",
                "timestamp": "2024-03-05T15:45:00Z",
            },
        ],
        "correct_ranking": [2, 4, 1, 3, 5],
    },
    {
        "emails": [
            {
                "id": 1,
                "subject": "Reminder: Team sync tomorrow 10 AM",
                "body": "Just a reminder that we have our weekly team sync tomorrow at 10 AM. Agenda: sprint review, blockers, planning.",
                "sender": "pm@company.com",
                "timestamp": "2024-04-01T17:00:00Z",
            },
            {
                "id": 2,
                "subject": "Investor due diligence documents — needed by 9 AM tomorrow",
                "body": "Series B investors are requesting financials, cap table, and IP documentation for due diligence. They need everything by 9 AM tomorrow. This is time-critical.",
                "sender": "cfo@company.com",
                "timestamp": "2024-04-01T18:00:00Z",
            },
            {
                "id": 3,
                "subject": "Customer complaint: billing error, threatening legal action",
                "body": "Customer ID #4821 has been double-charged for 3 months. They've contacted their attorney and are threatening a lawsuit if not resolved within 24 hours.",
                "sender": "billing-support@company.com",
                "timestamp": "2024-04-01T17:30:00Z",
            },
            {
                "id": 4,
                "subject": "Lunch delivery arriving at 12:30",
                "body": "Hey, just wanted to let you know that the lunch order for the design team is arriving at 12:30 today. Please be in the break room.",
                "sender": "office-admin@company.com",
                "timestamp": "2024-04-01T11:00:00Z",
            },
            {
                "id": 5,
                "subject": "New book recommendation: Atomic Habits",
                "body": "Finished Atomic Habits this weekend — highly recommend! Great ideas about building productive routines. Let me know if you want to borrow my copy.",
                "sender": "friend@gmail.com",
                "timestamp": "2024-04-01T10:00:00Z",
            },
        ],
        "correct_ranking": [2, 3, 1, 4, 5],
    },
]


# ─── Task 3: draft_reply (hard) ───────────────────────────────────────────────
# Each entry: {"email": {...}, "keywords": [...], "context": {...}}

DRAFT_REPLY_EMAILS: List[Dict[str, Any]] = [
    {
        "email": {
            "subject": "Proposal for Q2 Marketing Campaign Partnership",
            "body": (
                "Dear Marketing Team,\n\n"
                "I'm reaching out on behalf of BrandBoost Agency. We specialize in "
                "B2B demand generation and have driven 40% pipeline growth for clients "
                "in your sector.\n\n"
                "We'd love to explore a co-marketing partnership for your Q2 launch. "
                "Specifically, we're proposing joint webinars, co-authored whitepapers, "
                "and shared social media campaigns.\n\n"
                "Could we schedule a 30-minute call this week to discuss?\n\n"
                "Best regards,\nJames Chen\nBrandBoost Agency"
            ),
            "sender": "james.chen@brandboost.com",
            "timestamp": "2024-01-25T10:00:00Z",
        },
        "keywords": [
            "partnership", "co-marketing", "webinar", "whitepaper",
            "Q2", "campaign", "schedule", "call", "proposal",
        ],
        "context": {
            "instructions": (
                "Write a professional reply expressing interest in the partnership "
                "proposal and suggesting specific times for a discovery call."
            ),
        },
    },
    {
        "email": {
            "subject": "Bug Report: Data export feature producing corrupted CSV files",
            "body": (
                "Hi Support Team,\n\n"
                "We've discovered a critical bug in your data export feature. "
                "When we export more than 10,000 rows to CSV, the resulting file "
                "is corrupted — encoding errors and missing columns.\n\n"
                "This is blocking our weekly data pipeline. We're on the Enterprise plan "
                "and this is causing significant business impact.\n\n"
                "Ticket priority: HIGH. Please respond ASAP.\n\n"
                "Regards,\nPriya Nair\nData Engineering Lead, FinTrack Inc."
            ),
            "sender": "priya.nair@fintrack.com",
            "timestamp": "2024-01-26T14:30:00Z",
        },
        "keywords": [
            "bug", "CSV", "export", "corrupted", "encoding", "pipeline",
            "enterprise", "priority", "fix", "investigate", "workaround",
        ],
        "context": {
            "instructions": (
                "Write a professional support reply acknowledging the bug, "
                "apologizing for the impact, and explaining next steps for resolution."
            ),
        },
    },
    {
        "email": {
            "subject": "Request for Leave — 2 weeks from Jan 29",
            "body": (
                "Hi,\n\n"
                "I'd like to formally request annual leave from January 29th to February 9th "
                "(10 working days). I have 15 days of unused leave accrued.\n\n"
                "I've spoken with my teammates and they've agreed to cover my responsibilities "
                "during this period. I'll also prepare a handover document before I leave.\n\n"
                "Please let me know if this can be approved.\n\n"
                "Thank you,\nAlex Rivera"
            ),
            "sender": "alex.rivera@company.com",
            "timestamp": "2024-01-24T09:00:00Z",
        },
        "keywords": [
            "leave", "annual leave", "approved", "handover", "coverage",
            "January", "February", "working days", "accrued",
        ],
        "context": {
            "instructions": (
                "Write a manager's reply approving the leave request and confirming "
                "the dates and handover requirements."
            ),
        },
    },
    {
        "email": {
            "subject": "Vendor Invoice #INV-2024-0847 — Payment Due",
            "body": (
                "Dear Accounts Payable,\n\n"
                "Please find attached Invoice #INV-2024-0847 for services rendered "
                "in December 2023. Total amount: $14,750.00. Payment terms: Net 30.\n\n"
                "The due date is January 31, 2024. Please confirm receipt and expected "
                "payment date at your earliest convenience.\n\n"
                "Best regards,\nAccounts Receivable\nCloudServices Ltd."
            ),
            "sender": "ar@cloudservices.com",
            "timestamp": "2024-01-15T11:00:00Z",
        },
        "keywords": [
            "invoice", "payment", "due", "January", "confirm",
            "receipt", "processing", "net 30", "finance",
        ],
        "context": {
            "instructions": (
                "Write a professional reply confirming receipt of the invoice "
                "and providing an expected payment timeline."
            ),
        },
    },
]
