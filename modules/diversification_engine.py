def diversify_picks(picks):

    market_count = {}

    diversified = []

    for pick in picks:

        market = pick["market"]

        if market not in market_count:
            market_count[market] = 0

        if market_count[market] < 2:

            diversified.append(pick)

            market_count[market] += 1

    return diversified