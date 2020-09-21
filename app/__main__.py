"""https://github.com/guga31bb/nflfastR-data"""
from app.config import configure_logging
from app.jobs import (
    play_by_play,
    roster,
    rushing,
)


def main():
    # Raw Data
    play_by_play.run()
    roster.run()

    # Derived Data
    rushing.run()


if __name__ == "__main__":
    configure_logging()
    main()
