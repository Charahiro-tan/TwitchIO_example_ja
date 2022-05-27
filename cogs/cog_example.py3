"""
Cogのサンプル

TwitchIOにはCogという便利なクラスが用意されています。
これはイベントやコマンドをクラスにまとめて整理できる便利なクラスです。

このファイルは拡張子が.pyではないのでBotには読み込まれません。
"""
from twitchio.ext import commands


class CogExample(commands.Cog):
    # Cogクラスを継承してクラスを作ります

    def __init__(self, bot):
        # コンストラクタでmainのcommands.Botを受け取ります
        self.bot = bot

    # Cog内でイベントをリッスンするにはデコレーターを使用します
    # デコレーターにイベント名が渡されなかった時は関数名のイベントをリッスンします
    @commands.Cog.event()
    async def event_ready(self):
        print(f"{self.bot.nick}: 準備完了！")

    # クラス内で同じイベントをリッスンしたい時はデコレーターにイベント名を渡します
    @commands.Cog.event(event="event_message")
    async def hello(self, message):
        await message.channel.send(f"{message.author.display_name}さんこんにちは！")

    @commands.Cog.event(event="event_message")
    async def bye(self, message):
        await message.channel.send(f"{message.author.display_name}さんさようなら！")

    # コマンドを定義する時はcommands.commandデコレーターを使用します
    # デコレーターにコマンド名を(name= "echo")と渡すことができますが渡されなかった時は関数名が使われます。
    # デコレーターにエイリアスを渡すと別名を付けることができます(下の例ではechoでもecでも反応します)。
    # 呼びたされた時はcommands.Contextクラスが渡されます。
    # 引数を取りたい時は*argsでタプルで受け取ることができます(引数を取らない時は受け取らなくてOK)

    @commands.command(aliases=["ec"])
    async def echo(self, ctx, *args):
        if args:
            await ctx.reply(args[0])
        else:
            await ctx.reply("メッセージがありません！")


# commands.Botからload_moduleされた時に呼び出されるメソッド
# 引数のbotはcommands.Botクラスです。
def prepare(bot):
    bot.add_cog(CogExample(bot))
