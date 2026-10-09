from __future__ import annotations

from app.models.property import PropertyBase
from app.repositories.property import PropertyRepository


class PropertyService:
    def __init__(self, property_repo: PropertyRepository):
        self.property_repo = property_repo

    def create_property(
        self,
        owner_id: int,
        owner_role: str,
        title: str,
        location: str,
        property_type: str,
        description: str,
        price: float,
    ):
        if owner_role != "owner":
            raise ValueError("Only owners can create properties")
        cleaned_title = title.strip()
        cleaned_location = location.strip()
        if not cleaned_title or not cleaned_location:
            raise ValueError("Title and location are required")
        return self.property_repo.create(
            PropertyBase(
                title=cleaned_title,
                location=cleaned_location,
                property_type=property_type.strip() or "studio",
                description=description.strip(),
                price=float(price or 0),
                owner_id=owner_id,
            )
        )

    def search_properties(
        self,
        query: str = "",
        price_range: str = "",
        property_type: str = "",
    ) -> list:
        min_price = None
        max_price = None
        min_price_exclusive = False
        max_price_exclusive = False
        if price_range == "under-1500":
            max_price = 1500
            max_price_exclusive = True
        elif price_range == "1500-2500":
            min_price = 1500
            max_price = 2500
        elif price_range == "over-2500":
            min_price = 2500
            min_price_exclusive = True

        return self.property_repo.search(
            query=query.strip(),
            min_price=min_price,
            max_price=max_price,
            property_type=property_type.strip(),
            min_price_exclusive=min_price_exclusive,
            max_price_exclusive=max_price_exclusive,
        )

    def get_property(self, property_id: int):
        return self.property_repo.get_by_id(property_id)

    def list_owner_properties(self, owner_id: int):
        return self.property_repo.list_for_owner(owner_id)
