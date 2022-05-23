from typing import Optional

import attr


@attr.dataclass
class User:
    name: str
    email: str
    balance: Optional[int] = 0
    id: Optional[int] = None
