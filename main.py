import matplotlib
matplotlib.use("Agg")

from analyses.economic_resilience_hyperinflation import run as run_economic_resilience
from analyses.humanitarian_aid_prioritization import run as run_humanitarian_aid
from analyses.black_market_informal_economy import run as run_black_market_informal
from analyses.war_reconstruction_costs import run as run_war_reconstruction_costs


def main() -> None:
    run_economic_resilience()
    run_humanitarian_aid()
    run_black_market_informal()
    run_war_reconstruction_costs()


if __name__ == "__main__":
    main()
