class IntentRouter:
    def route(self, message):
        text = message.lower()

        if any(
            word in text
            for word in [
                "code",
                "coding",
                "python",
                "program",
                "debug",
                "bug",
            ]
        ):
            return "coding"

        if any(
            word in text
            for word in [
                "research",
                "research this",
                "find information",
                "look up",
            ]
        ):
            return "research"

        if any(
            word in text
            for word in [
                "plan",
                "planning",
                "roadmap",
                "organize",
            ]
        ):
            return "planning"

        if any(
            word in text
            for word in [
                "build a website",
                "make a website",
                "website",
                "web app",
            ]
        ):
            return "website"

        return "conversation"
