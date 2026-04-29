from dataclasses import dataclass


@dataclass(slots=True)
class _FormattingColor:
    foreground_name: str
    foreground_color: str
    background_color: str
    tag_name: str
    background_name: str = "<empty>"
    def __post_init__(self):
        if self.background_name == "<empty>":
            self.background_name = self.foreground_name

    def get(self, background: bool):
        if background:
            return self.background_color
        return self.foreground_color
