// OBSERVATORY_MARKET_MAP_V10_DATA_JS
window.OB_MARKET_DATA = window.OB_MARKET_DATA || {};

window.OB_MARKET_DATA.sectors = [
  {
    name: "Technology",
    constellationName: "Orion Circuit",
    strength: "Strong",
    read: "Technology is glowing. Money is flowing here, but that does not mean every name deserves your attention. Watch the leaders and respect crowding.",
    symbols: [
      { symbol: "AMD", tier: "hot", company: "Advanced Micro Devices", starName: "AMD Pulse", fact: "AMD often reacts strongly to semiconductor momentum and AI hardware sentiment.", role: "Momentum Watch", permission: "Paper Allowed · Live Locked", position: "Watched Candidate", tradeType: "Option-first", risk: "Moderate crowding", why: "OB is watching AMD because the technology constellation is strong and AMD is still responding to semiconductor appetite." },
      { symbol: "NVDA", tier: "hot", company: "NVIDIA", starName: "Nvidia Crown", fact: "NVDA often acts like a leadership star for AI-related market energy.", role: "Market Leader", permission: "Paper Allowed · Live Locked", position: "Watched Candidate", tradeType: "Option-first", risk: "High attention / crowding", why: "OB sees NVDA as a leadership star, but crowding must be respected before action." },
      { symbol: "MSFT", tier: "watch", company: "Microsoft", starName: "Microsoft Anchor", fact: "MSFT often behaves like a steadier institutional technology anchor.", role: "Anchor Star", permission: "Paper Allowed", position: "Watchlist", tradeType: "Stock or option", risk: "Calmer but slower", why: "OB is watching MSFT because it can confirm whether tech strength is broad or just concentrated in high-beta names." },
      { symbol: "AAPL", tier: "background", company: "Apple", starName: "Apple Core", fact: "AAPL often reflects consumer tech sentiment and mega-cap market mood.", role: "Background Giant", permission: "Watch Only", position: "Background", tradeType: "Stock watch", risk: "Not leading", why: "OB is not prioritizing AAPL right now because it is not one of the brightest stars in this constellation." },
      { symbol: "META", tier: "watch", company: "Meta Platforms", starName: "Meta Signal", fact: "META can move with ad market strength, AI spending, and platform sentiment.", role: "Attention Star", permission: "Paper Allowed", position: "Watchlist", tradeType: "Option possible", risk: "Momentum needs confirmation", why: "OB is watching META because attention is present, but the move needs cleaner confirmation." },
      { symbol: "AVGO", tier: "background", company: "Broadcom", starName: "Broadcom Gate", fact: "AVGO connects semiconductor infrastructure and networking strength.", role: "Infrastructure Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Not primary", why: "OB sees AVGO as part of the sky, but not the first star to inspect." }
    ]
  },
  {
    name: "Semiconductors",
    constellationName: "Silicon Arc",
    strength: "Strong",
    read: "Semiconductors are talking loud. Strength is here, but crowding can sneak in dressed like conviction. Pick clean stars, not loud stars.",
    symbols: [
      { symbol: "MU", tier: "hot", company: "Micron Technology", starName: "Micron Flare", fact: "MU can brighten when memory demand and semiconductor breadth improve.", role: "Momentum Leader", permission: "Paper Allowed · Live Locked", position: "Open / Review", tradeType: "Option premium mode", risk: "Moderate", why: "OB is watching MU because it is brightening with semiconductor strength without being the loudest crowded name." },
      { symbol: "AMD", tier: "watch", company: "Advanced Micro Devices", starName: "AMD Pulse", fact: "AMD often follows chip-sector appetite and risk-on technology behavior.", role: "Momentum Watch", permission: "Paper Allowed · Live Locked", position: "Watched Candidate", tradeType: "Option-first", risk: "Moderate crowding", why: "OB is watching AMD as a secondary semiconductor star that may confirm the sector move." },
      { symbol: "NVDA", tier: "hot", company: "NVIDIA", starName: "Nvidia Crown", fact: "NVDA is a high-attention leader and can make the whole sector feel hotter.", role: "Crowded Leader", permission: "Paper Allowed · Live Locked", position: "Watch / Caution", tradeType: "Option-first", risk: "Crowding elevated", why: "OB sees NVDA leading, but also carrying crowding pressure that can distort clean reads." },
      { symbol: "INTC", tier: "background", company: "Intel", starName: "Intel Relic", fact: "INTC can reflect legacy chip sentiment and turnaround expectations.", role: "Background Watch", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Weak follow-through", why: "OB is not prioritizing INTC because it is not leading the constellation." },
      { symbol: "SMCI", tier: "watch", company: "Super Micro Computer", starName: "Server Spark", fact: "SMCI can heat up when AI server and infrastructure themes run.", role: "Volatile Watch", permission: "Review Required", position: "Candidate Watch", tradeType: "Review only", risk: "Volatile", why: "OB is watching SMCI carefully because it can move fast, but it needs stronger permission and risk review." }
    ]
  },
  {
    name: "Energy",
    constellationName: "Solaris Rift",
    strength: "Weak",
    read: "Energy is dim right now. Do not try to save a weak constellation unless the setup proves itself first.",
    symbols: [
      { symbol: "XOM", tier: "watch", company: "Exxon Mobil", starName: "Exxon Ember", fact: "XOM often reflects oil-price expectations and energy-sector stability.", role: "Defensive Energy", permission: "Watch Only", position: "Watchlist", tradeType: "Stock watch", risk: "Sector weak", why: "OB keeps XOM visible because it is a steadier energy name, but the sector is not leading." },
      { symbol: "CVX", tier: "background", company: "Chevron", starName: "Chevron Stone", fact: "CVX can behave like a steadier integrated energy name.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Sector weak", why: "OB is not prioritizing CVX while the energy constellation is dim." },
      { symbol: "SLB", tier: "background", company: "SLB", starName: "Schlumberger Drill", fact: "SLB often responds to oilfield service demand and drilling activity.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Sector weak", why: "OB is leaving SLB in the background until the sector proves itself." },
      { symbol: "HAL", tier: "background", company: "Halliburton", starName: "Halliburton Spark", fact: "HAL can move with oil services and exploration expectations.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Sector weak", why: "OB is not chasing HAL while energy is faded." }
    ]
  },
  {
    name: "Consumer",
    constellationName: "Golden Arc",
    strength: "Strong",
    read: "Consumer names are holding up. Watch the leaders, but do not assume every retail star is clean.",
    symbols: [
      { symbol: "AMZN", tier: "hot", company: "Amazon", starName: "Amazon Comet", fact: "AMZN can move with retail strength, cloud expectations, and broad growth sentiment.", role: "Growth Consumer", permission: "Paper Allowed", position: "Candidate Watch", tradeType: "Option possible", risk: "Moderate", why: "OB is watching AMZN because it is a bright consumer growth star." },
      { symbol: "COST", tier: "watch", company: "Costco", starName: "Costco Shield", fact: "COST is often seen as a resilient consumer name.", role: "Defensive Leader", permission: "Watch Only", position: "Watchlist", tradeType: "Stock watch", risk: "Slow mover", why: "OB watches COST as a defensive strength check." },
      { symbol: "WMT", tier: "watch", company: "Walmart", starName: "Walmart Beacon", fact: "WMT can reflect defensive consumer strength.", role: "Defensive Watch", permission: "Watch Only", position: "Watchlist", tradeType: "Stock watch", risk: "Slow mover", why: "OB uses WMT to read consumer defense." },
      { symbol: "HD", tier: "background", company: "Home Depot", starName: "Home Depot Beam", fact: "HD can move with housing and renovation expectations.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Not leading", why: "OB is not prioritizing HD until it brightens." }
    ]
  },
  {
    name: "Financials",
    constellationName: "Vault Axis",
    strength: "Neutral",
    read: "Financials are not screaming yet. Wait for direction before treating this like a clean lane.",
    symbols: [
      { symbol: "JPM", tier: "watch", company: "JPMorgan Chase", starName: "JPM Vault", fact: "JPM often acts like a leadership name inside big banks.", role: "Bank Leader", permission: "Watch Only", position: "Watchlist", tradeType: "Stock watch", risk: "Neutral sector", why: "OB watches JPM as the financial leadership read." },
      { symbol: "BAC", tier: "background", company: "Bank of America", starName: "Bank Arc", fact: "BAC can react strongly to rate expectations and banking sentiment.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Neutral sector", why: "OB keeps BAC in the background until financials choose direction." },
      { symbol: "GS", tier: "background", company: "Goldman Sachs", starName: "Goldman Lens", fact: "GS can reflect investment banking and market activity expectations.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Neutral sector", why: "OB is not prioritizing GS yet." },
      { symbol: "MS", tier: "background", company: "Morgan Stanley", starName: "Morgan Signal", fact: "MS often connects wealth management and market sentiment.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Neutral sector", why: "OB is leaving MS as background context." }
    ]
  },
  {
    name: "Industrials",
    constellationName: "Iron Drift",
    strength: "Weak",
    read: "Industrials are faded. If you come here, come with proof, not hope.",
    symbols: [
      { symbol: "CAT", tier: "watch", company: "Caterpillar", starName: "Caterpillar Forge", fact: "CAT can reflect construction, mining, and industrial demand.", role: "Industrial Watch", permission: "Watch Only", position: "Watchlist", tradeType: "Stock watch", risk: "Weak sector", why: "OB watches CAT only as the strongest industrial read while the sector is weak." },
      { symbol: "BA", tier: "background", company: "Boeing", starName: "Boeing Wing", fact: "BA can move with aviation sentiment and company-specific news.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Company-specific risk", why: "OB is not prioritizing BA because it can carry company-specific noise." },
      { symbol: "DE", tier: "background", company: "Deere", starName: "Deere Field", fact: "DE often reflects agriculture and machinery demand.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Weak sector", why: "OB is waiting for DE to brighten before attention shifts." },
      { symbol: "GE", tier: "background", company: "GE Aerospace", starName: "GE Engine", fact: "GE can connect aviation, industrial, and energy themes.", role: "Background Star", permission: "Watch Only", position: "Background", tradeType: "Watch only", risk: "Weak sector", why: "OB is not prioritizing GE inside a faded industrial field." }
    ]
  }
];
