"""
その他

外部のAPIを叩く例と同期関数を使用したい時の例
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import TYPE_CHECKING, Dict, List

import logzero
from twitchio.ext import commands
from urltitle import URLTitleReader

if TYPE_CHECKING:
    from main import Bot
    from twitchio import Message

logger: logzero.logging = logzero.logger

url_re = re.compile(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]+")


class OtherCmds(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.session = None
        self.reader = URLTitleReader(verify_ssl=True)

    @commands.Cog.event()
    async def event_ready(self):
        """
        botで使ってるaiohttp.ClientSessionを使います
        aiohttpはなるべく使い回すのが定石らしいので
        """
        self.session = self.bot._http.session

    @commands.command()
    async def yuubin(self, ctx: commands.Context, *args):
        """
        郵便番号から住所を返すコマンド
        (手軽に使えるAPIが見当たらなかったので‥‥)
        株式会社アイビス様が提供しているAPIを利用させていただきます
        https://zipcloud.ibsnet.co.jp/doc/api

        URL: https://zipcloud.ibsnet.co.jp/api/search
        Params: zipcode 郵便番号
        """
        if not args:
            await ctx.reply("郵便番号を入力してください")

        URL = "https://zipcloud.ibsnet.co.jp/api/search"
        params = {"zipcode": args[0]}
        async with self.session.get(URL, params=params) as res:
            if res.status == 200:
                # await res.json()でもいけるはずですが、このAPIはmimetypeがtext/plainになっててできなかった‥‥
                _json = json.loads(await res.read())
            else:
                logger.error(f"yuubin error: status code {res.status}")
                return

        if _json["status"] == 200:
            results: List[Dict[str]] = _json["results"]
            address = []
            address_tmp = ""
            for res in results:
                for k, v in res.items():
                    if k.startswith("address"):
                        address_tmp += v
                address.append(address_tmp)
            await ctx.reply(f"この郵便番号は {' , '.join(address)} です！")
        else:
            logger.error(
                f"yuubin response error: code: {_json['status']} message: {_json['message']}"
            )

    @commands.Cog.event()
    async def event_message(self, message: Message):
        """
        コメントにURLが含まれてた時にタイトルを返す

        ここで使用するurltitleは同期ライブラリなので
        イベントループをブロックしないようにスレッドに逃がす必要があります

        ツイートのURLとか投げると本文がそのまま返ってくるので
        実際に使用するにはもう少し手を加えたほうがいいと思います
        """
        if message.echo:
            return

        result: List[str] = url_re.findall(message.content)
        if not result:
            return

        title_result = []
        for url in result:
            # clipはデフォで詳細出るので無視
            if "clips.twitch.tv" in url:
                continue
            else:
                # 同期ライブラリなのでスレッドに逃がす
                title = (
                    await asyncio.gather(asyncio.to_thread(self.reader.title, url))
                )[0]
                if title:
                    title_result.append(title)

        ctx: commands.Context = await self.bot.get_context(message)
        await ctx.reply(f"このURLは {' , '.join(title_result)} です！")


def prepare(bot: Bot):
    bot.add_cog(OtherCmds(bot))
