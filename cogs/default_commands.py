"""
コマンドの例
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

import logzero
from twitchio.ext import commands

if TYPE_CHECKING:
    from main import Bot
    from twitchio import FollowEvent, Message, User

logger: logzero.logging = logzero.logger

# fmt: off
COLOR = ["Red", "Blue", "Green", "SpringGreen", "HotPink", "BlueViolet", "CadetBlue", "Chocolate", "Coral", "DodgerBlue", "Firebrick", "GoldenRod", "OrangeRed", "YellowGreen", "SeaGreen"] # NOQA
# fmt: on


class DefaultCmds(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.streamer: User = None

    @commands.Cog.event()
    async def event_ready(self) -> None:
        self.streamer = (await self.bot.fetch_users(names=[self.bot.config.channel]))[0]

    @commands.command(aliases=["up"])
    async def uptime(self, ctx: commands.Context) -> None:
        """
        経過時間を返す。
        """
        try:
            stream = (await self.bot.fetch_streams(user_logins=[ctx.channel.name]))[0]
        except IndexError:
            await ctx.reply("配信中ではありません！")
            return
        uptime = datetime.datetime.now(datetime.timezone.utc) - stream.started_at
        m, s = divmod(uptime.seconds, 60)
        h, m = divmod(m, 60)
        if uptime.days:
            h += uptime.days * 24
        uptime_str = f"{h}:{format(m, '0>2')}:{format(s, '0>2')}"
        await ctx.reply(f"経過時間は {uptime_str} です！")

    @commands.command()
    async def color(self, ctx: commands.Context, *args) -> None:
        """
        Botのチャットでの色を変える。
        """
        if not ctx.author.is_broadcaster:
            return

        if not args:
            await ctx.reply(f"引数に色を指定してください。指定できる色: {' '.join(COLOR)}")
            return

        if args[0] in COLOR:
            await ctx.send(f"/color {args[0]}")
            await ctx.reply(f"色を{args[0]}に変更しました")
        else:
            await ctx.reply(f"無効な引数です。指定できる色: {' '.join(COLOR)}")

    @commands.command(aliases=["fa"])
    async def followage(self, ctx: commands.Context, *args) -> None:
        """
        チャンネルをフォローした期間を返す。
        ストリーマーは引数にユーザー名を指定するとそのユーザーがフォローした期間を返す。
        """
        from_user: User = None

        if ctx.author.is_broadcaster:
            if not args:
                return
            if ctx.channel.name == args[0]:
                return

            try:
                from_user = (await self.bot.fetch_users(names=[args[0]]))[0]
            except IndexError:
                await ctx.reply(f"{args[0]}さんは見つかりませんでした")
                return
        else:
            from_user = (await self.bot.fetch_users(names=[ctx.author.name]))[0]

        follow: FollowEvent = await from_user.fetch_follow(to_user=self.streamer)
        if not follow:
            await ctx.reply(
                f"{from_user.display_name}さんは{self.streamer.display_name}さんをフォローしていません！"
            )
            return

        JST = datetime.timezone(datetime.timedelta(hours=9), "Asia/Tokyo")
        followed_at = follow.followed_at.astimezone(JST)
        followed_at_str = followed_at.strftime("%Y/%m/%d %H:%M:%S")

        now = datetime.datetime.now(JST)
        diff = now - followed_at

        await ctx.reply(
            f"{from_user.display_name}さんが{self.streamer.display_name}さんをフォローしたのは{followed_at_str}です！フォローしてから{diff.days}日経過しました！"  # NOQA
        )

    @commands.command(aliases=["so"])
    async def shoutout(self, ctx: commands.Context, *args) -> None:
        """
        紹介コマンド
        """
        if not ctx.author.is_mod:
            return
        if args:
            user = args[0]
        else:
            user = ctx.message.tags.get("reply-parent-user-login")
            if not user:
                return

        msg = await self.get_introduction(user)
        if msg:
            await ctx.send(msg)

    async def get_introduction(self, user: str) -> Optional[str]:
        """
        チャンネル情報を取得して紹介文を返す
        """
        try:
            ch = await self.bot.fetch_channel(user.lower())
        except Exception as e:
            logger.error(e)
            return None

        message = f"素敵な{ch.user.name}さんのチャンネルもチェック！"
        if ch.game_name:
            message += f"{ch.user.name}さんの最後の配信は「{ch.title}」({ch.game_name})でした！"
        message += f" twitch.tv/{user.lower()}"
        return message


def prepare(bot: Bot):
    bot.add_cog(DefaultCmds(bot))
