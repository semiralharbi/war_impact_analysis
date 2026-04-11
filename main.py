import matplotlib
matplotlib.use("Agg")

from analyses.economic_resilience_hyperinflation import run as run_economic_resilience
from analyses.black_market_informal_economy import run as run_black_market_informal


def main() -> None:
    run_economic_resilience()
    run_black_market_informal()


if __name__ == "__main__":
    main()
