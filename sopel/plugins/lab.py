"""Get information about the lab."""

from ocflib.lab.stats import staff_in_lab
from ocflib.lab.stats import users_in_lab_count

from sopel import plugin


@plugin.rule(r"is ([a-z]+) in the lab")
def in_lab(bot, trigger):
    """Check if a staffer is in the lab."""
    username = trigger.group(2).strip()
    for session in staff_in_lab():
        if username == session.user:
            bot.reply(f"{username} is in the lab")
            break
    else:
        bot.reply(f"{username} is not in the lab")


def _prevent_ping(staffer):
    """Hack to prevent pinging the person by inserting a zero-width no-break space in their name."""
    return staffer[0] + "\u2060" + staffer[1:]


@plugin.rule(r"(who is|who's) in the lab", r"(?i)w+i+t+l+")
def who_is_in_lab(bot, trigger):
    """Report on who is currently in the lab."""
    staff = {session.user for session in staff_in_lab()}
    total = users_in_lab_count()

    if total != 1:
        are_number_people = f"are {total} people"
    else:
        are_number_people = "is 1 person"

    if staff:
        staff_list = ": {}".format(
            ", ".join(sorted(_prevent_ping(staffer) for staffer in staff))
        )
    else:
        staff_list = ""

    bot.reply(
        "there {} in the lab, including {} staff{}".format(
            are_number_people,
            len(staff),
            staff_list,
        ),
    )
