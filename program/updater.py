import os
import re
import sys
import asyncio
import subprocess
from asyncio import sleep

from git import Repo
from pyrogram.types import Message
from driver.filters import command
from pyrogram import Client, filters
from os import system, execle, environ
from driver.decorators import sudo_users_only
from git.exc import InvalidGitRepositoryError
from config import UPSTREAM_REPO, BOT_USERNAME


def gen_chlog(repo, diff):
    upstream_repo_url = Repo().remotes[0].config_reader.get("url").replace(".git", "")
    ac_br = repo.active_branch.name
    ch_log = tldr_log = ""
    ch = f"<b>updates for <a href={upstream_repo_url}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    ch_tl = f"updates for {ac_br}:"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"\n\nš¬ <b>{c.count()}</b> š <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b>"
            f"<a href={upstream_repo_url.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> šØāš» <code>{c.author}</code>"
        )
        tldr_log += f"\n\nš¬ {c.count()} š [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] šØāš» {c.author}"
    if ch_log:
        return str(ch + ch_log), str(ch_tl + tldr_log)
    return ch_log, tldr_log


def updater():
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    ac_br = repo.active_branch.name
    if "upstream" in repo.remotes:
        ups_rem = repo.remote("upstream")
    else:
        ups_rem = repo.create_remote("upstream", UPSTREAM_REPO)
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    return bool(changelog)


@Client.on_message(command(["Ų­ŲÆŲ«", f"update@{BOT_USERNAME}"]) & ~filters.edited)
@sudo_users_only
async def update_repo(_, message: Message):
    chat_id = message.chat.id
    msg = await message.reply("ā¹ `Ų¬Ų§Ų± ŲŖŲ­ŲÆŁŲ« Ų§ŁŁŁŁŲ§ŲŖ` āŗ")
    update_avail = updater()
    if update_avail:
        await msg.edit("ā¹ Ų§ŁŲŖŁŁ Ų§ŁŲŖŲ­ŲÆŁŲ« \n\n Ų£Ų¹ŁŲÆ ŲŖŲ“ŲŗŁŁ Ų§ŁŲØŁŲŖ Ų ŁŲ¹Ų§ŲÆ ŁŲ“Ų·ŁŲ§ ŁŲ±Ų© Ų£Ų®Ų±Ł Ų®ŁŲ§Ł ŲÆŁŁŁŲ© ŁŲ§Ų­ŲÆŲ© āŗ")
        system("git pull -f && pip3 install -r requirements.txt")
        execle(sys.executable, sys.executable, "main.py", environ)
        return
    await msg.edit("bot is **up-to-date** with [main](https://github.com/Akzeam-sourse/moha/tree/main)", disable_web_page_preview=True)


@Client.on_message(command(["Ų§Ų¹Ų§ŲÆŁ Ų§ŁŲŖŲ“ŲŗŁŁ", f"restart@{BOT_USERNAME}"]) & ~filters.edited)
@sudo_users_only
async def restart_bot(_, message: Message):
    msg = await message.reply("`ā¹ Ų¬Ų§Ų±Ł Ų§Ų¹Ų§ŲÆŁ ŲŖŲ“ŲŗŁŁ Ų§ŁŲØŁŲŖ āŗ`")
    args = [sys.executable, "main.py"]
    await msg.edit("ā¹ Ų§Ų¹Ų§ŲÆŁ ŲŖŲ“ŲŗŁŁ Ų§ŁŲØŁŲŖ\n\n Ų§ŁŲ¢Ł ŁŁŁŁŁ Ų§Ų³ŲŖŲ®ŲÆŲ§Ł ŁŲ°Ų§ Ų§ŁŲØŁŲŖ ŁŲ±Ų© Ų£Ų®Ų±Ł āŗ")
    execle(sys.executable, *args, environ)
    return
