"""
Raidが来た時とBitsに反応する例

ちなみに収益化されたチャンネルを持ってない為Bitsは未テストです。
"""
from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING

import logzero
from twitchio.ext import commands

if TYPE_CHECKING:
    from main import Bot
    from twitchio import Channel, Message

logger: logzero.logging = logzero.logger


class EventNotice(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.bits_re = re.compile(r";bits=(\d+);")

    @commands.Cog.event(event="event_raw_usernotice")
    async def raid_introduction(self, channel: Channel, tags: dict) -> None:
        """
        Raidが来た時にsoコマンドと同じような内容を流す
        """
        msg_id = tags.get("msg-id", None)
        if msg_id == "raid":
            viewer_count: str = tags.get("msg-param-viewerCount", "?")
            display_name: str = tags.get("display-name")
            login_name: str = tags.get("login", None)
            name: str = None
            if not display_name:
                display_name = login_name

            if display_name.lower() == login_name:
                name = display_name
            else:
                name = f"{display_name}({login_name})"

            await channel.send(f"{name}さんが{viewer_count}人でRaidしてくれました！")

            try:
                raider_ch = await self.bot.fetch_channel(login_name)
            except Exception:
                logger.error(f"チャンネル情報の取得に失敗しました: {login_name}")
                return

            send_msg = f"{name}さんRaidありがとうございます！"
            if raider_ch.title:
                s = f"{name}さんの最後の配信は「{raider_ch.title}」"
                if raider_ch.game_name:
                    s += f"({raider_ch.game_name})"
                send_msg += s + "でした！"
            send_msg += f" twitch.tv/{login_name}"

            await channel.send(send_msg)

            # n秒後にもう一度流す(流れてしまうかもしれないので)
            await asyncio.sleep(30)
            send_msg = send_msg.replace("Raidありがとうございます", "Raidありがとうございました")
            await channel.send(send_msg)

    @commands.Cog.event(event="event_message")
    async def on_bits(self, message: Message) -> None:
        """
        Bitsに反応する例
        """
        is_bits = self.bits_re.search(message.raw_data)
        if is_bits:
            ctx = await self.bot.get_context(message)
            await ctx.reply(
                f"{message.author.display_name}さん{is_bits.group(1)}bitsありがとうございます！"
            )


def prepare(bot: Bot):
    bot.add_cog(EventNotice(bot))
