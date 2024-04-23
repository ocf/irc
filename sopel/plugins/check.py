"""Show information about OCF users."""

import grp
import string

from ocflib.account import search
from ocflib.infra import ldap
from sopel import plugin


GROUP_COLOR_MAPPING = {
    "ocf": "\x0314",  # gray
    "sorry": "\x0304",  # red
    "opstaff": "\x0303",  # green
    "ocfstaff": "\x0302",  # blue
    "ocfroot": "\x0307",  # orange
    "ocfapphost": "\x0310",  # cyan
    "ocfofficers": "\x0306",  # purple
    "ocfalumni": "\x0313",  # pink
}


@plugin.command("check")
def check(bot, trigger):
    """Print information about an OCF user."""
    user = trigger.group(1).strip()
    attrs = search.user_attrs(user)

    if attrs is not None:
        groups = [grp.getgrgid(attrs["gidNumber"]).gr_name]
        groups.extend(
            sorted(group.gr_name for group in grp.getgrall() if user in group.gr_mem),
        )
        groups = [
            "{}{}\x0f".format(GROUP_COLOR_MAPPING.get(group, ""), group)
            for group in groups
        ]

        if "creationTime" in attrs:
            created = attrs["creationTime"].strftime("%Y-%m-%d")
        else:
            created = "unknown"

        bot.reply(
            "{user} ({uid}) | {name} | created {created} | groups: {groups}".format(
                user=user,
                uid=attrs["uidNumber"],
                name=attrs["cn"][0],
                created=created,
                groups=", ".join(groups),
            ),
            ping=False,
        )
    else:
        bot.reply(f"{user} does not exist", ping=False)


def alphanum(word):
    return "".join(c for c in word.lower() if c in string.ascii_lowercase)


@plugin.command("checkacct")
def checkacct(bot, trigger):
    """Print matching OCF usernames."""
    search_term = trigger.group(1).strip()
    keywords = search_term.split()

    if len(keywords) > 0:
        search = "(&{})".format(
            "".join(
                # all keywords must match either uid or cn
                "(|(uid=*{keyword}*)(cn=*{keyword}*))".format(
                    keyword=alphanum(keyword),
                )
                for keyword in keywords
            ),
        )

        with ldap.ldap_ocf() as c:
            c.search(
                ldap.OCF_LDAP_PEOPLE,
                search,
                attributes=("uid", "cn"),
                size_limit=5,
            )

            if len(c.response) > 0:
                bot.reply(
                    ", ".join(
                        sorted(
                            "{} ({})".format(
                                entry["attributes"]["uid"][0],
                                entry["attributes"]["cn"][0],
                            )
                            for entry in c.response
                        ),
                    ),
                )
            else:
                bot.reply("no results found")
