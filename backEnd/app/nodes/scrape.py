import httpx
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
from pprint import pprint


class Lead(BaseModel):
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None


class ScrapeNode:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # search url = 0 credits
        self.search_url = "https://api.apollo.io/v1/people/search"
        # Match requires specific identifiers to unlock the record - uses credits
        self.match_url = "https://api.apollo.io/v1/people/match"
        self.headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}

    async def get_verified_leads(
        self, industry: str, location: str, limit: int = 10
    ) -> List[Lead]:
        leads = []
        payload = {
            "api_key": self.api_key,
            "q_organization_domains_list": [industry],  # or use industry_tag_ids
            "person_locations": [location],
            "per_page": limit,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.search_url, json=payload, headers=self.headers
            )
            pprint(resp.json().keys())
            results = resp.json().get("people") or []

            for person in results:
                lead = Lead(
                    id=person.get("id"),
                    first_name=person.get("first_name"),
                    last_name=person.get("last_name"),
                    email=person.get("email"),
                    title=person.get("title"),
                    company_name=person.get("organization", {}).get("name"),
                    website_url=person.get("organization", {}).get("website"),
                    linkedin_url=person.get("linkedin_url"),
                )
                leads.append(lead)
