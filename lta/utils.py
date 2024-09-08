from random import Random
from uuid import UUID


def make_uuid4(rand: Random) -> UUID:
    return UUID(int=rand.getrandbits(128), version=4)
