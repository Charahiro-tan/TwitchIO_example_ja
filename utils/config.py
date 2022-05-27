from dataclasses import dataclass


@dataclass
class Config:
    token: str = ""
    channel: str = ""
    prefix: str = ""
    loglevel: int = 20

    @property
    def initial_channel(self):
        return [self.channel]

    @property
    def irc_login(self):
        return {
            "token": self.token,
            "initial_channels": self.initial_channel,
            "prefix": self.prefix,
        }
