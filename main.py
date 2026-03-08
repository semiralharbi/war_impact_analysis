import matplotlib
matplotlib.use("Agg")

from analyses.economic_resilience_hyperinflation import run as run_economic_resilience
from analyses.poverty_and_food_insecurity import run as run_poverty_food_insecurity
from analyses.black_market_informal_economy import run as run_black_market_informal
from analyses.war_reconstruction_costs import run as run_war_reconstruction_costs


def main() -> None:
    run_economic_resilience()
    run_poverty_food_insecurity()
    run_black_market_informal()
    run_war_reconstruction_costs()


if __name__ == "__main__":
    main()
