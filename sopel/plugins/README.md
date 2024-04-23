# plugins

To port things from ircbot...

- replace `msg.match` with `trigger`
- replace `msg.respond` with `bot.reply`
  - if `ping=False` in the `msg.respond` replace it with `bot.say`
- add any extra python packages needed to the dockerfile (`pipx inject`)
- add the plugin to `.transpire.py` along with the others
