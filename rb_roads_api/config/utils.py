import os
from dataclasses import dataclass, asdict


@dataclass
class RBEnviron:
    rb_src: str = os.getenv("RB_SRC")
    rb_data: str = os.getenv("RB_DATA")


@dataclass
class ComputeParams:
    outfn: str = os.path.join(RBEnviron.rb_src, "output/justpopResult.txt")
    tons_per_person: float = 4.50
    lat: float = 33.781
    lon: float = -84.388
    stride: float = 0.009
    radius: float = 75000
    zoom: float = 0.5
    nthreads: int = 8

    def asdict(self):
        return asdict(self)

    @property
    def formatted_dict(self):
        return {
            "-f": self.outfn,
            "-t": self.tons_per_person,
            "--lat": self.lat, "--lon": self.lon,
            "--radius": self.stride,
            "--zoom": self.zoom,
            "--stride": self.stride,
            "--nthreads": self.nthreads
        }

    def __str__(self):
        return " ".join([f"{k} {v}" for k, v in self.formatted_dict.items()])

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for k, v in self.formatted_dict.items():
            yield k, v

    @property
    def command(self):
        cmd = ["/bin/bash", "-c",
               os.path.join(RBEnviron.rb_src, "justPop.exe")]
        for k, v in self.formatted_dict.items():
            cmd.append(f'{k}')
            cmd.append(f'{v}')
        return cmd


@dataclass
class RBRoadsJob:
    status: Literal["started", "failed", "complete"]
    message: str
    params: Dict | ComputeParams
    command: Dict | List | str
    poptable_output_file: os.PathLike | str
    exit_code: int | str | None
    output_stream: Any

    def asdict(self):
        return asdict(self)