SYMBOL_METADATA = {
    "AAPL": {
        "name": "Apple Inc.",
        "blurb": "Apple designs consumer electronics, software, and services, with major exposure to iPhone, wearables, and services revenue."
    },
    "ABNB": {
        "name": "Airbnb, Inc.",
        "blurb": "Airbnb operates a global travel marketplace focused on short-term stays, experiences, and alternative accommodations."
    },
    "AMZN": {
        "name": "Amazon.com, Inc.",
        "blurb": "Amazon is a diversified platform spanning e-commerce, cloud computing, logistics, advertising, and consumer devices."
    },
    "AAPL": {
        "name": "Apple Inc.",
        "blurb": "Apple designs consumer electronics, software, and services, with major exposure to iPhone, wearables, and services revenue."
    },
    "COIN": {
        "name": "Coinbase Global, Inc.",
        "blurb": "Coinbase is a crypto exchange and infrastructure company whose performance is heavily tied to digital asset activity and sentiment."
    },
    "COP": {
        "name": "ConocoPhillips",
        "blurb": "ConocoPhillips is an upstream energy producer with exposure to oil and gas prices, global production trends, and commodity cycles."
    },
    "CRM": {
        "name": "Salesforce, Inc.",
        "blurb": "Salesforce is an enterprise software company focused on CRM, automation, cloud applications, and AI-enabled workflows."
    },
    "CVX": {
        "name": "Chevron Corporation",
        "blurb": "Chevron is a global energy major with exposure to upstream production, refining, and global commodity pricing."
    },
    "EOG": {
        "name": "EOG Resources, Inc.",
        "blurb": "EOG is an oil and gas producer with performance tied to commodity prices, production efficiency, and capital discipline."
    },
    "MPC": {
        "name": "Marathon Petroleum Corporation",
        "blurb": "Marathon Petroleum is a downstream energy company focused on refining, logistics, and fuel distribution economics."
    },
    "MU": {
        "name": "Micron Technology, Inc.",
        "blurb": "Micron is a semiconductor memory company exposed to DRAM and NAND cycles, AI demand, and broader chip pricing dynamics."
    },
    "NFLX": {
        "name": "Netflix, Inc.",
        "blurb": "Netflix is a subscription streaming company driven by content engagement, pricing power, and subscriber monetization."
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "blurb": "NVIDIA is a semiconductor and AI infrastructure leader with major exposure to GPUs, data centers, and AI compute demand."
    },
    "OXY": {
        "name": "Occidental Petroleum Corporation",
        "blurb": "Occidental is an energy producer with sensitivity to crude pricing, production strategy, and carbon management themes."
    },
    "PANW": {
        "name": "Palo Alto Networks, Inc.",
        "blurb": "Palo Alto Networks is a cybersecurity platform company focused on network, cloud, and security operations protection."
    },
    "PLTR": {
        "name": "Palantir Technologies Inc.",
        "blurb": "Palantir provides data analytics and AI software platforms for government and commercial customers."
    },
    "PSX": {
        "name": "Phillips 66",
        "blurb": "Phillips 66 is an energy manufacturing and logistics company with refining, midstream, and chemicals exposure."
    },
    "PYPL": {
        "name": "PayPal Holdings, Inc.",
        "blurb": "PayPal is a digital payments platform exposed to transaction growth, merchant adoption, and consumer spending behavior."
    },
    "ROKU": {
        "name": "Roku, Inc.",
        "blurb": "Roku is a streaming platform business tied to connected TV usage, advertising demand, and platform monetization."
    },
    "UBER": {
        "name": "Uber Technologies, Inc.",
        "blurb": "Uber operates mobility and delivery marketplaces with performance driven by engagement, take rates, and operating leverage."
    },
    "VLO": {
        "name": "Valero Energy Corporation",
        "blurb": "Valero is a downstream energy business tied to refining margins, fuel demand, and commodity input spreads."
    },
    "XLE": {
        "name": "Energy Select Sector SPDR Fund",
        "blurb": "XLE is an ETF tracking major U.S. energy companies and is often used as a liquid proxy for large-cap energy exposure."
    },
    "XOM": {
        "name": "Exxon Mobil Corporation",
        "blurb": "Exxon Mobil is an integrated energy major with exposure across upstream, downstream, and global energy markets."
    },
}

def get_symbol_meta(symbol: str):
    symbol = (symbol or "").upper()
    return SYMBOL_METADATA.get(symbol, {
        "name": f"{symbol} Company",
        "blurb": "Company profile not yet added. This symbol page is ready for a richer research blurb."
    })
