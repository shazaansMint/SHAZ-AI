
import logging


class PermissionService:
    def __init__(self):
        self.logger = logging.getLogger(
            "shaz.permissions"
        )

        self.rules = {
            "read": "allowed",
            "calculate": "allowed",
            "search": "allowed",
            "write": "confirm",
            "execute": "confirm",
            "delete": "confirm",
            "external": "confirm",
        }

    def check(self, action):
        decision = self.rules.get(
            action,
            "blocked",
        )

        self.logger.info(
            "Permission check | action=%s decision=%s",
            action,
            decision,
        )

        return decision

    def is_allowed(self, action):
        return self.check(action) == "allowed"

    def requires_confirmation(self, action):
        return self.check(action) == "confirm"

    def is_blocked(self, action):
        return self.check(action) == "blocked"
