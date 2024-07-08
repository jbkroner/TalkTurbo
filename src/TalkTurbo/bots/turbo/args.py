import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Turbo")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode", dest="debug"
    )

    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        help=(
            "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random,"
            " while lower values like 0.2 will make it more focused and deterministic."
        ),
        dest="temperature",
    )

    parser.add_argument(
        "-m",
        "--max-response-length",
        type=int,
        help="Max response length in tokens",
        dest="max_response_length",
    )

    parser.add_argument(
        "--sync-app-commands",
        action="store_true",
        help="Sync app commands with discord during the bot startup",
        dest="sync_app_commands",
    )

    parser.add_argument(
        "--no-user-identifiers",
        action="store_true",
        help="If set then hashed user identifiers will not be included in requests to the OpenAI API.",
        dest="no_user_identifiers",
    )

    parser.add_argument(
        "--logging-level",
        type=str,
        default="INFO",
        help="Logging level. Choose DEBUG, INFO, WARNING, or ERROR.  Defaults to INFO",
        dest="logging_level",
    )

    parser.add_argument(
        "--dalle-timeout",
        type=int,
        default=60,
        help="dalle timeout in seconds",
        dest="dalle_timeout",
    )

    parser.add_argument(
        "--disable-image-storage",
        action="store_true",
        help="Do not store generated Dalle images.",
        dest="disable_image_storage",
    )

    parser.add_argument(
        "--pre-load-context",
        help="Pre-load the context with pre-load.yaml",
        default="pre-load.yaml",
    )

    return parser.parse_args()
