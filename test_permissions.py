from core.permissions.permission_service import (
    PermissionService,
)


def main():
    permissions = PermissionService()

    actions = [
        "read",
        "calculate",
        "write",
        "execute",
        "delete",
        "unknown",
    ]

    for action in actions:
        print(
            f"{action} -> "
            f"{permissions.check(action)}"
        )


if __name__ == "__main__":
    main()
