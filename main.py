from __future__ import annotations

import os
from typing import TYPE_CHECKING, List

import logzero
import toml
from twitchio.ext import commands

from utils import Config

if TYPE_CHECKING:
    from twitchio import Channel, Message, User


logger: logzero.logging = logzero.logger

__ver__ = "1.0.0"


class Bot(commands.Bot):
    def __init__(self, config: Config) -> None:
        self.config = config

        # case_insensitive=True にしておくとコマンドの大文字小文字が関係なくなる
        super().__init__(**self.config.irc_login, case_insensitive=True)

        # ./cogs内の.pyファイルをcogとして登録する
        if not self.cogs:
            cogs = self.get_cogs()
            for cog in cogs:
                self.load_module(cog)
                logger.info(f"{cog.removeprefix('cogs.')} を読み込みました")

    def get_cogs(self) -> List[str]:
        """
        ./cogs内の.pyファイルをリストで返す
        """
        cog_files = os.listdir("./cogs")
        return [
            f'cogs.{file.removesuffix(".py")}'
            for file in cog_files
            if file.endswith(".py")
        ]

    async def event_channel_joined(self, channel: Channel) -> None:
        """
        ただの準備完了のお知らせ
        """
        logger.info(f"{channel.name}に接続しました")

    async def event_message(self, message: Message) -> None:
        """
        メッセージのログ用
        """
        if message.echo:
            logger.info(f"[{message.channel.name}]{self.nick}: {message.content}")
            return
        logger.info(
            f"[{message.channel.name}]{message.author.display_name}: {message.content}"
        )

        # 親クラスでevent_messageからコマンドを呼び出しているので、
        # 子クラスでオーバーライドするときはこれやらないとコマンドが呼び出されない。
        # 子クラスでmessage.echoをreturnしてるなら
        # await self.handle_commands(message)
        # でもいいと思います。
        await super().event_message(message)

    async def event_command_error(
        self, context: commands.Context, error: Exception
    ) -> None:
        """
        コマンドが見つからなかったりエラーが起きると呼び出されるメソッド。
        親クラスのprint文が気になるので。お好みで。
        """
        logger.error(f"コマンドエラー: {error}")

    @commands.command()
    async def ver(self, ctx: commands.Context) -> None:
        await ctx.reply(f"バージョン: {__ver__}")


if __name__ == "__main__":
    config = Config(**toml.load("config.toml"))

    # loggerの設定
    # 個人的な好みでlogzeroを使用します
    logzero.setup_logger(isRootLogger=True, level=config.loglevel)

    bot = Bot(config)
    bot.run()
