"""Appointment-confirmation SMS bot: sends reminders, reads replies, escalates what it cannot classify.

The sender is injected, so this runs offline. Swap FakeSender for a Twilio client in production.
"""
import re
from dataclasses import dataclass, field
from datetime import time

QUIET_START, QUIET_END = time(21, 0), time(8, 0)

CONFIRM = re.compile(r"\b(yes|y|confirm|confirmed|ok|see you)\b", re.I)
RESCHEDULE = re.compile(r"\b(reschedule|move|change|another time)\b", re.I)
CANCEL = re.compile(r"\b(cancel|stop)\b", re.I)


def in_quiet_hours(now: time) -> bool:
    return now >= QUIET_START or now < QUIET_END


def classify_reply(text: str) -> str:
    """Return 'confirm', 'reschedule', 'cancel' or 'escalate'. Cancel wins over everything."""
    if CANCEL.search(text):
        return "cancel"
    if RESCHEDULE.search(text):
        return "reschedule"
    if CONFIRM.search(text):
        return "confirm"
    return "escalate"


@dataclass
class FakeSender:
    sent: list = field(default_factory=list)

    def send(self, phone: str, body: str) -> None:
        self.sent.append((phone, body))


@dataclass
class Appointment:
    phone: str
    when: str
    status: str = "pending"


class ConfirmationBot:
    def __init__(self, sender, now: time):
        self.sender = sender
        self.now = now
        self.appointments: dict[str, Appointment] = {}
        self.escalations: list[tuple[str, str]] = []

    def remind(self, appt_id: str, appt: Appointment) -> bool:
        if in_quiet_hours(self.now):
            return False  # hold until the morning window
        self.appointments[appt_id] = appt
        self.sender.send(appt.phone, f"Reminder: appointment {appt.when}. Reply YES to confirm or RESCHEDULE.")
        return True

    def handle_reply(self, phone: str, text: str) -> str:
        appt = next((a for a in self.appointments.values() if a.phone == phone), None)
        if appt is None:
            self.escalations.append((phone, text))
            return "escalate"
        intent = classify_reply(text)
        if intent == "escalate":
            self.escalations.append((phone, text))  # a person looks at it
            return intent
        appt.status = {"confirm": "confirmed", "reschedule": "reschedule_requested", "cancel": "cancelled"}[intent]
        return intent
