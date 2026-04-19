from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping
from uuid import uuid4


@dataclass
class FakePaymentGateway:
    """Pasarela de cobro simulada (equivalente conceptual a la del monolito)."""

    def charge(
        self,
        amount: Decimal,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        _ = (amount, metadata)
        return f"fake_{uuid4()}"
