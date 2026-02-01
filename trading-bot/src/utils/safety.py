"""
VAYU Trading Bot - Safety Module
=================================
Critical safety features:
- Local kill switch (file-based)
- Stale data detection
- Rate limiting
- Emergency stops
"""

import os
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Expand paths
VAYU_DIR = Path.home() / ".vayu"
KILL_FILE = VAYU_DIR / "KILL"
STATE_DB = VAYU_DIR / "state.db"
CONFIG_PATH = VAYU_DIR / "config.yaml"


class KillSwitch:
    """
    Multi-channel kill switch:
    1. Local file: ~/.vayu/KILL
    2. Discord command (via webhook polling)
    3. Emergency stop on critical errors
    """
    
    def __init__(self):
        self.killed = False
        self.kill_reason = None
        self._ensure_state_db()
    
    def _ensure_state_db(self):
        """Initialize SQLite database."""
        if not STATE_DB.exists():
            # Run schema
            schema_path = Path(__file__).parent / ".." / ".." / ".." / ".vayu" / "schema.sql"
            if schema_path.exists():
                with sqlite3.connect(STATE_DB) as conn:
                    with open(schema_path) as f:
                        conn.executescript(f.read())
    
    def check(self) -> tuple[bool, Optional[str]]:
        """
        Check if kill signal is active.
        
        Returns:
            (is_killed, reason)
        """
        if self.killed:
            return True, self.kill_reason
        
        # Check local file
        if KILL_FILE.exists():
            self.killed = True
            self.kill_reason = f"Local kill file detected: {KILL_FILE}"
            self._log_event("kill_switch", "critical", self.kill_reason)
            return True, self.kill_reason
        
        return False, None
    
    def trigger(self, reason: str, source: str = "manual"):
        """
        Trigger emergency stop.
        
        Args:
            reason: Why the kill was triggered
            source: 'manual', 'circuit_breaker', 'error', 'system'
        """
        self.killed = True
        self.kill_reason = f"[{source}] {reason}"
        
        # Create kill file
        KILL_FILE.write_text(f"{datetime.now().isoformat()}\n{reason}\n{source}\n")
        
        # Log to database
        self._log_event("kill_switch", "critical", reason, {"source": source})
        
        logger.critical(f"🚨 KILL SWITCH ACTIVATED: {reason}")
    
    def reset(self, confirm: bool = False) -> bool:
        """
        Reset kill switch after manual review.
        
        Args:
            confirm: Must pass True to prevent accidental resets
        
        Returns:
            True if reset successful
        """
        if not confirm:
            logger.warning("Kill switch reset requires confirm=True")
            return False
        
        self.killed = False
        self.kill_reason = None
        
        # Remove kill file
        if KILL_FILE.exists():
            KILL_FILE.unlink()
        
        self._log_event("kill_switch_reset", "info", "Kill switch manually reset")
        logger.info("✅ Kill switch reset")
        return True
    
    def _log_event(self, event_type: str, severity: str, message: str, details: Dict = None):
        """Log event to database."""
        try:
            with sqlite3.connect(STATE_DB) as conn:
                conn.execute(
                    """INSERT INTO system_events (event_type, severity, message, details)
                       VALUES (?, ?, ?, ?)""",
                    (event_type, severity, message, str(details) if details else None)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log event: {e}")


class DataValidator:
    """
    Validates price data freshness and integrity.
    """
    
    def __init__(self, stale_threshold_sec: int = 30):
        self.stale_threshold = stale_threshold_sec
        self.last_valid_timestamp = None
        self.consecutive_stale = 0
        self.max_consecutive_stale = 3  # Kill after 3 stale reads
    
    def validate(self, timestamp: datetime, current_time: Optional[datetime] = None) -> tuple[bool, str]:
        """
        Check if data is fresh.
        
        Args:
            timestamp: Data timestamp
            current_time: Reference time (default: now)
        
        Returns:
            (is_valid, reason)
        """
        if current_time is None:
            current_time = datetime.now()
        
        age_sec = (current_time - timestamp).total_seconds()
        
        if age_sec < 0:
            # Future timestamp - clock skew?
            return False, f"Future timestamp detected (clock skew?): {age_sec:.1f}s ahead"
        
        if age_sec > self.stale_threshold:
            self.consecutive_stale += 1
            
            if self.consecutive_stale >= self.max_consecutive_stale:
                return False, f"Data stale for {self.consecutive_stale} consecutive reads (> {self.stale_threshold}s old)"
            
            return False, f"Stale data: {age_sec:.1f}s old (threshold: {self.stale_threshold}s)"
        
        # Valid data
        self.last_valid_timestamp = timestamp
        self.consecutive_stale = 0
        return True, "OK"
    
    def get_last_valid_age(self) -> Optional[float]:
        """Get age of last valid data in seconds."""
        if self.last_valid_timestamp is None:
            return None
        return (datetime.now() - self.last_valid_timestamp).total_seconds()


class RateLimiter:
    """
    Track API calls and enforce rate limits.
    """
    
    def __init__(self, max_requests_per_min: int = 120):
        self.max_requests = max_requests_per_min
        self.window_sec = 60
        self.calls = []  # List of timestamps
    
    def can_call(self) -> bool:
        """Check if API call is allowed."""
        now = time.time()
        
        # Remove old calls outside window
        cutoff = now - self.window_sec
        self.calls = [t for t in self.calls if t > cutoff]
        
        return len(self.calls) < self.max_requests
    
    def record_call(self, endpoint: str, success: bool = True, error: str = None):
        """Record an API call."""
        now = time.time()
        self.calls.append(now)
        
        # Log to database
        try:
            with sqlite3.connect(STATE_DB) as conn:
                conn.execute(
                    """INSERT INTO api_calls (endpoint, success, error_message)
                       VALUES (?, ?, ?)""",
                    (endpoint, success, error)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")
    
    def get_remaining(self) -> int:
        """Get remaining calls in current window."""
        now = time.time()
        cutoff = now - self.window_sec
        self.calls = [t for t in self.calls if t > cutoff]
        return max(0, self.max_requests - len(self.calls))
    
    def get_wait_time(self) -> float:
        """Get seconds to wait before next call is allowed."""
        if self.can_call():
            return 0.0
        
        if not self.calls:
            return 0.0
        
        oldest = min(self.calls)
        wait = (oldest + self.window_sec) - time.time()
        return max(0.0, wait)


class EmergencyStop:
    """
    Central emergency stop coordinator.
    Combines all safety checks.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.kill_switch = KillSwitch()
        self.data_validator = DataValidator(
            stale_threshold_sec=self.config.get('stale_data_threshold_sec', 30)
        )
        self.rate_limiter = RateLimiter(
            max_requests_per_min=self.config.get('rate_limit_requests_per_min', 120)
        )
        self.errors_in_window = 0
        self.max_errors = 10  # Kill after 10 errors in 5 minutes
        self.error_window_sec = 300
        self.error_times = []
    
    def check_all(self, data_timestamp: Optional[datetime] = None) -> tuple[bool, str]:
        """
        Run all safety checks.
        
        Returns:
            (should_stop, reason)
        """
        # 1. Check kill switch
        is_killed, reason = self.kill_switch.check()
        if is_killed:
            return True, reason
        
        # 2. Check data freshness
        if data_timestamp:
            is_valid, reason = self.data_validator.validate(data_timestamp)
            if not is_valid:
                self._record_error(f"Data validation: {reason}")
                # Don't immediately kill on single stale - validator handles consecutive
                if "consecutive" in reason.lower():
                    self.kill_switch.trigger(reason, "stale_data")
                    return True, reason
        
        # 3. Check error rate
        if self._check_error_rate():
            reason = f"Error rate exceeded: {self.errors_in_window} errors in {self.error_window_sec}s"
            self.kill_switch.trigger(reason, "error_rate")
            return True, reason
        
        # 4. Check rate limit
        if not self.rate_limiter.can_call():
            wait = self.rate_limiter.get_wait_time()
            return True, f"Rate limit exceeded. Wait {wait:.1f}s"
        
        return False, "OK"
    
    def _record_error(self, error: str):
        """Record error for rate tracking."""
        now = time.time()
        self.error_times.append(now)
        
        # Remove old errors
        cutoff = now - self.error_window_sec
        self.error_times = [t for t in self.error_times if t > cutoff]
        self.errors_in_window = len(self.error_times)
        
        logger.error(f"Safety error recorded: {error}")
    
    def _check_error_rate(self) -> bool:
        """Check if error rate exceeds threshold."""
        now = time.time()
        cutoff = now - self.error_window_sec
        self.error_times = [t for t in self.error_times if t > cutoff]
        self.errors_in_window = len(self.error_times)
        
        return self.errors_in_window >= self.max_errors


if __name__ == "__main__":
    # Test safety module
    print("Testing VAYU Safety Module")
    print("=" * 50)
    
    # Test kill switch
    ks = KillSwitch()
    killed, reason = ks.check()
    print(f"Kill switch active: {killed}")
    
    # Test data validator
    dv = DataValidator(stale_threshold_sec=30)
    
    # Valid data
    valid, msg = dv.validate(datetime.now())
    print(f"Fresh data check: {valid} ({msg})")
    
    # Stale data
    old_time = datetime.now() - timedelta(seconds=60)
    valid, msg = dv.validate(old_time)
    print(f"Stale data check: {valid} ({msg})")
    
    # Test rate limiter
    rl = RateLimiter(max_requests_per_min=60)
    print(f"Rate limit remaining: {rl.get_remaining()}")
    rl.record_call("test")
    print(f"After 1 call: {rl.get_remaining()}")
    
    print("\n✅ Safety module tests complete")
