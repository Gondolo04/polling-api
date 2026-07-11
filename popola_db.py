"""
popola_db.py — Demo data seed script for the Polling API.

Clears all existing data and repopulates with realistic demo content.
Run from the project root with:
    python popola_db.py

Make sure the Django server is NOT running when you execute this,
and that migrations have already been applied.
"""

import os
import sys
import django

# ── Django setup ─────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import User
from polls.models import Poll, Choice, Vote

# ── 1. Clear existing data (order matters — delete dependents first) ──────────
print("Clearing existing data...")
Vote.objects.all().delete()
Choice.objects.all().delete()
Poll.objects.all().delete()
User.objects.all().delete()
print("  ✓ All tables cleared.\n")

# ── 2. Create users ───────────────────────────────────────────────────────────
print("Creating users...")

superuser = User.objects.create_superuser(
    username="superuser_demo",
    email="superuser@example.com",
    password="superuser12345",
)
# create_superuser sets is_staff and is_superuser; role stays default "user"
# this account is only for /admin/ panel access

admin = User.objects.create_user(
    username="admin_demo",
    email="admin@example.com",
    password="admin12345",
    role="admin",
)

mod = User.objects.create_user(
    username="mod_demo",
    email="mod@example.com",
    password="mod12345",
    role="moderator",
)

user1 = User.objects.create_user(
    username="user_demo",
    email="user@example.com",
    password="user12345",
    role="user",
)

user2 = User.objects.create_user(
    username="alice_demo",
    email="alice@example.com",
    password="alice12345",
    role="user",
)

print("  ✓ 5 users created.\n")

# ── 3. Create polls and choices ───────────────────────────────────────────────
print("Creating polls and choices...")

# Poll 1 — open, created by user_demo, has votes
poll1 = Poll.objects.create(
    title="Favorite season?",
    description="Which season do you prefer?",
    created_by=user1,
    is_open=True,
)
c1_1 = Choice.objects.create(poll=poll1, text="Spring")
c1_2 = Choice.objects.create(poll=poll1, text="Summer")
c1_3 = Choice.objects.create(poll=poll1, text="Autumn")
c1_4 = Choice.objects.create(poll=poll1, text="Winter")

# Poll 2 — open, created by mod_demo, has votes
poll2 = Poll.objects.create(
    title="Best back-end language?",
    description="For a REST API project like this one.",
    created_by=mod,
    is_open=True,
)
c2_1 = Choice.objects.create(poll=poll2, text="Python")
c2_2 = Choice.objects.create(poll=poll2, text="JavaScript / Node")
c2_3 = Choice.objects.create(poll=poll2, text="Java")
c2_4 = Choice.objects.create(poll=poll2, text="Go")

# Poll 3 — CLOSED, created by admin_demo, has votes
# Useful for testing: voting on this should return a 400 "poll is closed"
poll3 = Poll.objects.create(
    title="Preferred work style?",
    description="How do you prefer to work day-to-day?",
    created_by=admin,
    is_open=False,
)
c3_1 = Choice.objects.create(poll=poll3, text="Fully remote")
c3_2 = Choice.objects.create(poll=poll3, text="Fully in office")
c3_3 = Choice.objects.create(poll=poll3, text="Hybrid")

# Poll 4 — open, created by alice_demo, has some votes
poll4 = Poll.objects.create(
    title="Favorite coffee drink?",
    description="Pick your go-to order.",
    created_by=user2,
    is_open=True,
)
c4_1 = Choice.objects.create(poll=poll4, text="Espresso")
c4_2 = Choice.objects.create(poll=poll4, text="Cappuccino")
c4_3 = Choice.objects.create(poll=poll4, text="Americano")
c4_4 = Choice.objects.create(poll=poll4, text="Latte")

# Poll 5 — open, created by user_demo, NO votes yet
# Good for the grader to test voting through the HTML client or HTTPie
poll5 = Poll.objects.create(
    title="Best Italian city to visit?",
    description="Where would you most like to spend a weekend?",
    created_by=user1,
    is_open=True,
)
c5_1 = Choice.objects.create(poll=poll5, text="Rome")
c5_2 = Choice.objects.create(poll=poll5, text="Florence")
c5_3 = Choice.objects.create(poll=poll5, text="Milan")
c5_4 = Choice.objects.create(poll=poll5, text="Venice")

print("  ✓ 5 polls created (4 open, 1 closed).\n")

# ── 4. Create votes ───────────────────────────────────────────────────────────
# Rule enforced by the model: one vote per user per poll (unique_together).
# So each user appears at most once per poll here.
print("Creating votes...")

# Poll 1 — Favorite season (4 votes)
Vote.objects.create(poll=poll1, choice=c1_1, user=user1)   # user_demo → Spring
Vote.objects.create(poll=poll1, choice=c1_2, user=user2)   # alice_demo → Summer
Vote.objects.create(poll=poll1, choice=c1_3, user=mod)     # mod_demo → Autumn
Vote.objects.create(poll=poll1, choice=c1_1, user=admin)   # admin_demo → Spring

# Poll 2 — Best back-end language (3 votes)
Vote.objects.create(poll=poll2, choice=c2_1, user=user1)   # user_demo → Python
Vote.objects.create(poll=poll2, choice=c2_1, user=user2)   # alice_demo → Python
Vote.objects.create(poll=poll2, choice=c2_2, user=admin)   # admin_demo → JS/Node

# Poll 3 — Preferred work style, CLOSED (3 votes)
# Demonstrates that a closed poll still shows results correctly
Vote.objects.create(poll=poll3, choice=c3_1, user=user1)   # user_demo → Remote
Vote.objects.create(poll=poll3, choice=c3_3, user=user2)   # alice_demo → Hybrid
Vote.objects.create(poll=poll3, choice=c3_1, user=mod)     # mod_demo → Remote

# Poll 4 — Coffee (2 votes, leaving room for test voting)
Vote.objects.create(poll=poll4, choice=c4_2, user=user1)   # user_demo → Cappuccino
Vote.objects.create(poll=poll4, choice=c4_1, user=mod)     # mod_demo → Espresso

# Poll 5 — Italian city: intentionally 0 votes — ready for live testing

print("  ✓ 12 votes created across 4 polls.\n")

# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 60)
print("✓  Database populated successfully!")
print("=" * 60)

print("""
DEMO ACCOUNTS
─────────────────────────────────────────────────────────────
  superuser_demo / superuser12345  →  Django superuser (/admin/)
  admin_demo     / admin12345      →  API role: admin  (ban/unban users)
  mod_demo       / mod12345        →  API role: moderator (manage any poll)
  user_demo      / user12345       →  API role: user
  alice_demo     / alice12345      →  API role: user

DEMO POLLS
─────────────────────────────────────────────────────────────
  1. "Favorite season?"            OPEN    4 votes
  2. "Best back-end language?"     OPEN    3 votes
  3. "Preferred work style?"       CLOSED  3 votes  ← test closed poll errors here
  4. "Favorite coffee drink?"      OPEN    2 votes
  5. "Best Italian city to visit?" OPEN    0 votes  ← ready to test voting

TIP: Poll 5 has no votes — use it to test the full vote flow
     through the HTML client or HTTPie.
     Try voting on Poll 3 to see the "poll is closed" 400 error.
""")