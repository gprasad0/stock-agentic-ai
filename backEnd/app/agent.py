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
    headers = {
        "x-api-key": os.getenv("APOLLO_API_KEY"),
        "Content-Type": "application/json",
    }
    payload = {
        "q_organization_industry_tag_ids": [state["industry"]],
        "q_organization_locations": [state["location"]],
        "per_page": 10,
    }
    response = requests.post(
        "https://api.apollo.io/v1/mixed_people/search", json=payload, headers=headers
    )
    leads = response.json().get("people", [])
    cleaned = [
        {
            "name": lead.get("name"),
            "email": lead.get("email"),
            "company": lead.get("organization", {}).get("name"),
            "website": lead.get("organization", {}).get("website_url"),
            "title": lead.get("title"),
        }
        for lead in leads
        if lead.get("email")
    ]
    return {"leads": cleaned}


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
