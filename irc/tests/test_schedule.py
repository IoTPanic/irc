import random
import datetime

import pytest

from irc import schedule


def test_delayed_command_order():
	"""
	delayed commands should be sorted by delay time
	"""
	null = lambda: None
	delays = [random.randint(0, 99) for x in range(5)]
	cmds = sorted([
		schedule.DelayedCommand(delay, null, tuple())
		for delay in delays
	])
	assert [c.delay.seconds for c in cmds] == sorted(delays)

def test_periodic_command_delay():
	"A PeriodicCommand must have a positive, non-zero delay."
	with pytest.raises(ValueError) as exc_info:
		schedule.PeriodicCommand(0, None, None)
	assert str(exc_info.value) == test_periodic_command_delay.__doc__

def test_periodic_command_fixed_delay():
	"""
	Test that we can construct a periodic command with a fixed initial
	delay.
	"""
	fd = schedule.PeriodicCommandFixedDelay.at_time(
		at = datetime.datetime.now(),
		delay = datetime.timedelta(seconds=2),
		function = lambda: None,
		arguments = [],
		)
	assert fd.due() == True
	assert fd.next().due() == False

class TestCommands(object):
	def test_command_at_noon(self):
		"""
		Create a periodic command that's run at noon every day.
		"""
		when = datetime.time(12,0)
		daily = datetime.timedelta(days=1)
		# convert when to the next datetime matching this time
		when = datetime.datetime.combine(datetime.date.today(), when)
		if when < datetime.datetime.now():
			when += daily
		cmd = schedule.PeriodicCommandFixedDelay.at_time(
			when, daily, function=None, arguments=None)
		assert cmd.due() is False
		next_cmd = cmd.next()
		day_from_now = datetime.datetime.now() + daily
		two_days_from_now = day_from_now + daily
		assert day_from_now < next_cmd < two_days_from_now