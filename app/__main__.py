"""https://github.com/guga31bb/nflfastR-data"""
from app.config import configure_logging
from app.jobs import (
    rushing_by_player,
    play_by_play,
    roster
)


def main():
    # Raw Data
    play_by_play.run()
    roster.run()

    # Derived Data
    rushing_by_player.run()


if __name__ == "__main__":
    configure_logging()
    main()
