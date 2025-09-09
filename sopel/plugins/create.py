"""Approve accounts."""

import ssl
import textwrap
import threading
import time
from traceback import format_exc

from sopel import plugin
from sopel.config import types
from celery import Celery
from celery import exceptions
from celery.events import EventReceiver
from kombu import Connection
from ocflib.account.submission import get_tasks

IRC_CHANNELS_ANNOUNCE = "#administrivia"
IRC_CHANNELS_OPER = "#root"

tasks = None



class CelerySection(types.StaticSection):
    broker = types.SecretAttribute("broker", str)
    backend = types.SecretAttribute("backend", str)


def setup(bot):
    bot.settings.define_section("celery", CelerySection)

    def add_thread(func):
        def thread_func():
            try:
                func(bot)
            except Exception as ex:
                error_msg = "ircbot exception in thread {thread}.{function}: {exception}".format(
                    thread=func.__module__,
                    function=func.__name__,
                    exception=ex,
                )
                bot.say(error_msg, "#rebuild")
                bot.handle_error(
                    textwrap.dedent(
                        """
                    {error}

                    {traceback}
                    """,
                    ).format(
                        error=error_msg,
                        traceback=format_exc(),
                    ),
                )
            # For now, just let it fail silently. We should consider uncommenting this block.
            # finally:
            # The thread has stopped, probably because it threw an error
            # This shouldn't happen, so we stop the entire bot
            # os._exit(1)

        thread = threading.Thread(target=thread_func, daemon=True)
        thread.start()

    add_thread(celery_listener)


@plugin.command("approve")
@plugin.require_admin(reply=True)
def approve(bot, trigger):
    """Approve a pending account."""
    user_name = trigger.group(1)
    tasks.approve_request.delay(user_name)
    bot.reply(f"approved {user_name}, the account is being created")


@plugin.command("reject")
@plugin.require_admin(reply=True)
def reject(bot, trigger):
    """Reject a pending account."""
    user_name = trigger.group(1)
    tasks.reject_request.delay(user_name)
    bot.reply(f"rejected {user_name}, better luck next time")


@plugin.command("list")
@plugin.require_admin(reply=True)
def list_pending(bot, trigger):
    """List accounts pending approval."""
    task = tasks.get_pending_requests.delay()
    try:
        task.wait(timeout=5)
        if task.result:
            for request in task.result:
                bot.reply(request)
        else:
            bot.reply("no pending requests")
    except exceptions.TimeoutError:
        bot.reply("timed out loading list of requests, sorry!")


def celery_listener(bot):
    """Listen for events from Celery, relay to IRC."""
    global tasks

    while len(bot.channels.keys()) <= 0:
        time.sleep(2)

    celery = Celery(
        broker=bot.settings.celery.broker,
        backend=bot.settings.celery.backend,
    )
    celery.conf.broker_use_ssl = {
        "ssl_ca_certs": "/etc/ssl/certs/ca-certificates.crt",
        "ssl_cert_reqs": ssl.CERT_REQUIRED,
    }
    # `redis_backend_use_ssl` is an OCF patch which was proposed upstream:
    # https://github.com/celery/celery/pull/3831
    celery.conf.redis_backend_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE,
    }

    # TODO: stop using pickle
    celery.conf.task_serializer = "pickle"
    celery.conf.result_serializer = "pickle"
    celery.conf.accept_content = {"pickle"}

    tasks = get_tasks(celery)

    connection = Connection(
        bot.settings.celery.broker,
        ssl={
            "ssl_ca_certs": "/etc/ssl/certs/ca-certificates.crt",
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
        },
        transport="redis"
    )

    def bot_announce(targets, message):
        for target in targets:
            bot.say(message, target)

    def on_account_created(event):
        request = event["request"]

        if request["calnet_uid"]:
            uid_or_gid = "Calnet UID: {}".format(request["calnet_uid"])
        elif request["callink_oid"]:
            uid_or_gid = "Callink OID: {}".format(request["callink_oid"])
        else:
            uid_or_gid = "No Calnet UID or OID set"

        bot_announce(
            IRC_CHANNELS_ANNOUNCE,
            "{user} created ({real_name}, {uid_or_gid})".format(
                user=request["user_name"],
                real_name=request["real_name"],
                uid_or_gid=uid_or_gid,
            ),
        )

    def on_account_submitted(event):
        request = event["request"]
        bot_announce(
            IRC_CHANNELS_OPER,
            "{user} ({real_name}) needs approval: {reasons}".format(
                user=request["user_name"],
                real_name=request["real_name"],
                reasons=", ".join(request["reasons"]),
            ),
        )

    def on_account_approved(event):
        request = event["request"]
        bot_announce(
            IRC_CHANNELS_ANNOUNCE,
            "{user} was approved, now pending creation.".format(
                user=request["user_name"],
            ),
        )

    def on_account_rejected(event):
        request = event["request"]
        bot_announce(
            IRC_CHANNELS_ANNOUNCE,
            "{user} was rejected.".format(
                user=request["user_name"],
            ),
        )

    while True:
        with connection as conn:
            recv = EventReceiver(
                conn,
                app=celery,
                handlers={
                    "ocflib.account_created": on_account_created,
                    "ocflib.account_submitted": on_account_submitted,
                    "ocflib.account_approved": on_account_approved,
                    "ocflib.account_rejected": on_account_rejected,
                },
            )
            recv.capture(limit=None, timeout=None)
