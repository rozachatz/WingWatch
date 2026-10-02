"""Record antenna commands for demo replay without opening a hardware socket."""


class SimulatedRotatorClient:
    def __init__(self) -> None:
        self.commands: list[tuple[float, float]] = []

    async def execute(self, azimuth: float, elevation: float) -> None:
        self.commands.append((float(azimuth), float(elevation)))

    @property
    def last_command(self) -> tuple[float, float] | None:
        return self.commands[-1] if self.commands else None

    def reset(self) -> None:
        self.commands.clear()
