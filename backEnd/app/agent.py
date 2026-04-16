from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv(override=True)


class OutreachState(TypedDict):
    industry: str
    location: str
    leads: List[dict]
    enriched_leads: List[dict]
    emails: List[dict]


def scrape_node(state: OutreachState):
    # Apollo logic comes next
    return {"leads": []}


def enrich_node(state: OutreachState):
    # Website scraping comes next
    return {"enriched_leads": []}


def generate_node(state: OutreachState):
    # LLM email generation comes next
    return {"emails": []}


def save_node(state: OutreachState):
    # Save to JSON comes next
    return {}


# Wire it up
graph = StateGraph(OutreachState)
graph.add_node("scrape", scrape_node)
graph.add_node("enrich", enrich_node)
graph.add_node("generate", generate_node)
graph.add_node("save", save_node)

graph.set_entry_point("scrape")
graph.add_edge("scrape", "enrich")
graph.add_edge("enrich", "generate")
graph.add_edge("generate", "save")
graph.add_edge("save", END)

app = graph.compile()

# Test run
result = app.invoke(
    {
        "industry": "real estate",
        "location": "Bengaluru",
        "leads": [],
        "enriched_leads": [],
        "emails": [],
    }
)

print(result)
