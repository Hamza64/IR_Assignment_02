DEFAULT_SEEDS = [
    "https://www.investopedia.com/terms/f/freight-forwarder.asp",
    "https://www.techtarget.com/searcherp/definition/freight-forwarder",
    "https://www.shipbob.com/blog/incoterms/",
    "https://www.marineinsight.com/know-more/what-is-bill-of-lading/",
    "https://www.flexport.com/glossary/",
]
DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; FreightIntelIR/1.0; +https://example.com/academic-project)"
DEFAULT_MAX_PAGES = 25
DEFAULT_CRAWL_DEPTH = 1
DEFAULT_TIMEOUT = 12
STOPWORDS_EXTRA = [
    "shipping", "freight", "cargo", "logistics", "transport", "maersk"
]
TOPIC_KEYWORDS = {
    "incoterms": ["incoterm", "incoterms", "fob", "cif", "exw", "ddp"],
    "documentation": ["bill of lading", "awb", "invoice", "document", "paperwork"],
    "customs": ["customs", "clearance", "duty", "tariff", "compliance"],
    "containers": ["container", "reefer", "fcl", "lcl", "teu"],
    "ports": ["port", "vessel", "terminal", "berth", "congestion"],
    "supply_chain": ["supply chain", "lead time", "disruption", "inventory", "route"],
}
SAMPLE_QUERIES = [
    "what is a freight forwarder",
    "difference between fcl and lcl",
    "what is bill of lading",
    "incoterms in international shipping",
    "port congestion impact on shipments",
    "customs clearance process",
]
