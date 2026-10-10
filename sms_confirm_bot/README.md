# SMS appointment-confirmation bot

Sends a reminder, reads the reply, and acts on it. Anything the bot cannot classify is escalated to a person instead of guessed at.

- **Quiet hours:** reminders between 9 pm and 8 am are held, not sent.
- **Reply intent:** confirm, reschedule, or cancel. If a reply mentions both confirming and cancelling, cancel wins, because that is the safer outcome.
- **Escalation:** unknown phone numbers and unclassifiable replies are queued for a human.
- **Sender:** `FakeSender` records messages. A Twilio sender would implement the same `send(phone, body)` method.

Files: `bot.py`, `test_bot.py`

Run: `python3 -m unittest`
