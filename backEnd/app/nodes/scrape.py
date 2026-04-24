import httpx
import logging
from typing import List, Optional
from pydantic import BaseModel


# Lead Model
class Lead(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: Optional[str]
    company_name: str
    website_url: str  # Mandatory for our enrichment
    title: str


class ScrapeNode:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}

    async def get_verified_leads(
        self, industry: str, location: str, volume: int
    ) -> List[Lead]:
        leads = []

        # 1. SEARCH PHASE (Cost: 0 Credits)
        search_url = "https://api.apollo.io/v1/people/search"
        payload = {
            "api_key": self.api_key,
            "q_organization_domains_list": [industry],  # or use industry_tag_ids
            "person_locations": [location],
            "per_page": volume,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(search_url, json=payload, headers=self.headers)
            results = resp.json().get("people", [])

            for person in results:
                # 2. OPTIMIZATION: Only process if they have a website for Node 2
                website = person.get("organization", {}).get("website_url")
                if not website:
                    continue

                lead_data = {
                    "id": person.get("id"),
                    "first_name": person.get("first_name"),
                    "last_name": person.get("last_name"),
                    "email": person.get("email"),
                    "company_name": person.get("organization", {}).get("name"),
                    "website_url": website,
                    "title": person.get("title"),
                }

                # 3. REVEAL LOGIC (Cost: 1 Credit if email is missing)
                if not lead_data["email"] or "hidden" in lead_data["email"]:
                    lead_data["email"] = await self.reveal_email(client, person)

                if lead_data["email"]:
                    leads.append(Lead(**lead_data))

        return leads

    async def reveal_email(
        self, client: httpx.AsyncClient, person: dict
    ) -> Optional[str]:
        """Calls the Match endpoint to spend 1 credit and get the real email."""
        match_url = "https://api.apollo.io/v1/people/match"

        # Match requires specific identifiers to unlock the record
        payload = {
            "api_key": self.api_key,
            "id": person.get("id"),
            "first_name": person.get("first_name"),
            "last_name": person.get("last_name"),
            "organization_name": person.get("organization", {}).get("name"),
        }

        try:
            resp = await client.post(match_url, json=payload, headers=self.headers)
            match_data = resp.json().get("person", {})
            return match_data.get("email")
        except Exception as e:
            logging.error(f"Failed to reveal email for {person.get('id')}: {e}")
            return None
