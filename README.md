# TwitchIOの実装例
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/Charahiro-tan/TwitchIO_example_ja)  
冗長な部分もあると思うので参考程度で‥‥  
  
Python3.9未満では動作しないと思います  
動作確認済み Python 3.10.4  
  
### ファイル構成
```
┣ main.py　             メイン
┣ example_config.toml   config.tomlにリネームして設定ファイルとして使います
┣ timer.toml            タイマー設定用
┣ utils
┃ ┗ config.py           config用のdataclass
┗ cogs                  (このフォルダの.pyファイルはBotにCogとして登録されます)
  ┣ commands.json       custom_commands保存用JSON
  ┣ cog_example.py3     Cogの説明。拡張子がpy3なのでこれはBotに無視されます
  ┣ custom_commands.py  コマンドでコマンドを登録する例
  ┣ default_commands.py よくあるコマンド的な
  ┣ event_notice.py     RaidとBitsに反応する例
  ┣ other_commands.py   外部のAPIを叩くコマンドと同期処理ライブラリを使用する例
  ┗ timer.py            一定時間ごとにコメントを送信する例
```
  
### メッセージの送信について
ほとんどのメソッドでメッセージを送信する時に
```python
await ctx.reply("...")
```
を使用していますが、普通に送信したい場合は以下のようにしてください
```python
# Contextの場合
await ctx.send("...")
# Messageの場合
await message.channel.send("...")
```
  

### I am...
[Twitter](https://twitter.com/__Charahiro)  
[Twitch](https://www.twitch.tv/charahiro_)