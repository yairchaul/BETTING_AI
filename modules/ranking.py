def ranking_edges(picks):

    ordenados = sorted(picks, key=lambda x: x["ev"], reverse=True)

    print("\n🔥 DAILY EDGE RANKING 🔥")

    for i,p in enumerate(ordenados[:10]):
        print(i+1, p["game"], "EV:", round(p["ev"]*100,2),"%")