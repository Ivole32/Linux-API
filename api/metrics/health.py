from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

@dataclass
class FluashHealth:
    success_count: int = 0
    error_count: int = 0
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    last_success: Optional[datetime] = None
    last_attempt: Optional[datetime] = None

    def record_success(self):
        self.success_count += 1
        self.consecutive_failures = 0
        self.last_success = datetime.now(timezone.utc)
        self.last_error = None

    def record_error(self, error: Exception):
        self.error_count += 1
        self.consecutive_failures += 1
        self.last_error = str(error)

    def record_attempt(self):
        self.last_attempt = datetime.now(timezone.utc)

    def error_rate(self) -> float:
        total = self.success_count + self.error_count
        return self.error_count / total if total else 0.0
    
flush_health = FluashHealth()