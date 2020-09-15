"""https://github.com/guga31bb/nflfastR-data"""
from app.config import configure_logging
from app.jobs import (
    play_by_play,
    roster,
)


def main():
    play_by_play.run()
    roster.run()


if __name__ == "__main__":
    configure_logging()
    main()
