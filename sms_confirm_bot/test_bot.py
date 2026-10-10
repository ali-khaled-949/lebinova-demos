import unittest
from datetime import time

from bot import Appointment, ConfirmationBot, FakeSender, classify_reply, in_quiet_hours

DAY = time(10, 0)
NIGHT = time(22, 30)


class BotTests(unittest.TestCase):
    def test_classify_replies(self):
        self.assertEqual(classify_reply("YES see you then"), "confirm")
        self.assertEqual(classify_reply("can we reschedule?"), "reschedule")
        self.assertEqual(classify_reply("please cancel"), "cancel")
        self.assertEqual(classify_reply("what's the parking like"), "escalate")

    def test_cancel_wins_over_confirm(self):
        self.assertEqual(classify_reply("yes but I need to cancel"), "cancel")

    def test_quiet_hours_hold_reminders(self):
        self.assertTrue(in_quiet_hours(NIGHT))
        self.assertFalse(in_quiet_hours(DAY))
        sender = FakeSender()
        bot = ConfirmationBot(sender, NIGHT)
        self.assertFalse(bot.remind("1", Appointment("+15550001", "Mon 9am")))
        self.assertEqual(sender.sent, [])

    def test_confirm_updates_status(self):
        sender = FakeSender()
        bot = ConfirmationBot(sender, DAY)
        bot.remind("1", Appointment("+15550001", "Mon 9am"))
        self.assertEqual(bot.handle_reply("+15550001", "yes"), "confirm")
        self.assertEqual(bot.appointments["1"].status, "confirmed")

    def test_unknown_reply_is_escalated(self):
        sender = FakeSender()
        bot = ConfirmationBot(sender, DAY)
        bot.remind("1", Appointment("+15550001", "Mon 9am"))
        self.assertEqual(bot.handle_reply("+15550001", "is it indoors?"), "escalate")
        self.assertEqual(bot.escalations, [("+15550001", "is it indoors?")])
        self.assertEqual(bot.appointments["1"].status, "pending")


if __name__ == "__main__":
    unittest.main()
