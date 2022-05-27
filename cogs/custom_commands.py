"""
コマンドでコマンドを定義する例
コマンドはcommands.jsonに保存します。

addcmd   : コマンド登録
editcmd  : コマンド編集
removecmd: コマンド削除
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict

import aiofiles
import logzero
from twitchio.ext import commands

if TYPE_CHECKING:
    from main import Bot

logger: logzero.logging = logzero.logger


class CustomCmds(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.cmd_json_path = "cogs/commands.json"
        self.default_cmds = []
        self.cmds = {}

    @commands.Cog.event()
    async def event_ready(self) -> None:
        """
        コードで定義されたコマンドを取得する(上書きを防ぐため)
        ↓
        JSON読み込み
        ↓
        JSONのコマンドを登録
        """
        for k, v in self.bot.commands.items():
            self.default_cmds.append(k)
            if v.aliases:
                self.default_cmds.append(*v.aliases)

        self.cmds = await self.json_read()
        self.custom_cmd_add()

    @commands.command()
    async def addcmd(self, ctx: commands.Context, *args) -> None:
        """
        コマンドを登録するコマンド
        構文: addcmd <コマンド名> <メッセージ>
        """
        if not ctx.author.is_mod:
            return
        if len(args) < 2:
            await ctx.reply(f"{self.bot._prefix}addcmd <コマンド名> <メッセージ> で登録できます")
            return

        name = args[0].removeprefix(self.bot._prefix)
        message = args[1]

        if name in self.default_cmds:
            await ctx.reply(f"{self.bot._prefix}{name} は登録できません。")
            return
        if name in self.cmds:
            await ctx.reply(f"コマンドを編集するときは{self.bot._prefix}editcmdを使用してください")
            return

        self.cmds[name] = message
        self.bot.add_command(commands.Command(name=name, func=self.get_reply))
        await self.json_write()
        await ctx.reply(f"{self.bot._prefix}{name}を登録しました")

    @commands.command()
    async def editcmd(self, ctx: commands.Context, *args) -> None:
        """
        登録されてるコマンドを編集するコマンド
        構文: editcmd <コマンド名> <メッセージ>
        """
        if not ctx.author.is_mod:
            return
        if len(args) < 2:
            await ctx.reply(f"{self.bot._prefix}editcmd <コマンド名> <メッセージ> で編集できます")
            return

        name = args[0].removeprefix(self.bot._prefix)
        message = args[1]

        if name not in self.cmds:
            await ctx.reply(f"{self.bot._prefix}{name} は登録されていません")
            return

        self.cmds[name] = message
        self.bot.remove_command(name)
        self.bot.add_command(commands.Command(name=name, func=self.get_reply))
        await self.json_write()
        await ctx.reply(f"{self.bot._prefix}{name} のメッセージを更新しました")

    @commands.command()
    async def removecmd(self, ctx: commands.Context, *args) -> None:
        """
        登録されたコマンドを削除するコマンド
        構文: <コマンド名>
        """
        if not ctx.author.is_mod:
            return
        if not args:
            await ctx.reply(f"{self.bot._prefix}removecmd <コマンド名> で削除できます")
            return

        name = args[0].removeprefix(self.bot._prefix)

        if name not in self.cmds:
            await ctx.reply(f"{self.bot._prefix}{name} は登録されていません")
            return

        del self.cmds[name]
        self.bot.remove_command(name)
        await self.json_write()
        await ctx.reply(f"{self.bot._prefix}{name} を削除しました")

    async def get_reply(self, ctx: commands.Context) -> None:
        """
        コマンド応答用
        """
        reply = self.cmds.get(ctx.command.name)
        if reply:
            await ctx.reply(reply)

    def custom_cmd_add(self) -> None:
        """
        self.cmdsのコマンドを登録する
        """
        if self.cmds:
            for cmd in self.cmds.keys():
                self.bot.add_command(commands.Command(name=cmd, func=self.get_reply))

    def custom_cmd_remove(self) -> None:
        """
        self.cmdsのコマンドを削除する
        """
        if self.cmds:
            for cmd in self.cmds.keys():
                self.bot.remove_command(cmd)

    async def json_read(self) -> Dict:
        """
        JSONを読み込む
        """
        async with aiofiles.open(self.cmd_json_path, "r") as f:
            return json.loads(await f.read())

    async def json_write(self) -> None:
        """
        self.cmdsをJSONに書き込む
        """
        async with aiofiles.open(self.cmd_json_path, "w") as f:
            await f.write(json.dumps(self.cmds, indent=4))


def prepare(bot: Bot):
    bot.add_cog(CustomCmds(bot))
