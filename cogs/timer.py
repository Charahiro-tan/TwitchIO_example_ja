"""
一定間隔でメッセージを流す例
timer.tomlで設定した内容を流す。
reloadコマンドでtimer.tomlを再読み込みする。
"""
from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

import aiofiles
import logzero
import toml
from twitchio.ext import commands

if TYPE_CHECKING:
    from main import Bot

logger: logzero.logging = logzero.logger


@dataclass
class TimerConfig:
    interval: int = 0
    message: str = ""

    @property
    def message_list(self) -> List:
        """
        messageを行ごとに分割してリストで返す

        空の行を削除&もし同じメッセージがあった時に排除したいので一旦setにしてます
        """
        _list = self.message.splitlines()
        _set = set([s for s in _list if s != ""])
        return list(_set)


class Timer(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.config_path = "timer.toml"
        self.config = TimerConfig(**toml.load(self.config_path))
        self.timer_id = None
        self.channel = None

    @commands.Cog.event()
    async def event_ready(self) -> None:
        """
        タイマースタート
        """
        self.channel = self.bot.get_channel(self.bot.config.channel)

        asyncio.create_task(self.timer())

    @commands.command()
    async def reload(self, ctx: commands.Context) -> None:
        """
        timer.tomlをリロードするコマンド
        """
        self.timer_id = time.time()
        async with aiofiles.open(self.config_path, "r") as f:
            self.config = TimerConfig(**toml.loads(await f.read()))

        asyncio.create_task(self.timer())

    async def timer(self) -> None:
        """
        タイマー本体
        """
        message_list = self.config.message_list.copy()
        message_list_len = len(message_list)
        if not message_list_len:
            return
        if not self.config.interval:
            return

        sended_msg = ""

        while True:
            if not message_list:
                message_list = self.config.message_list.copy()
            send_msg = message_list.pop(random.randrange(len(message_list)))
            if send_msg == sended_msg:
                if message_list_len != 1 and message_list:
                    msg = message_list.pop(random.randrange(len(message_list)))
                    message_list.append(send_msg)
                    send_msg = msg
            sended_msg = send_msg

            await self.channel.send(send_msg)

            now = time.time()
            self.timer_id = now
            id = await asyncio.sleep(self.config.interval * 60, now)

            if self.timer_id != id:
                break


def prepare(bot: Bot):
    bot.add_cog(Timer(bot))
