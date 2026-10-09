from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select

from app.models.property import Property, PropertyBase


class PropertyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, property_data: PropertyBase) -> Property:
        property_db = Property.model_validate(property_data)
        self.db.add(property_db)
        self.db.commit()
        self.db.refresh(property_db)
        return property_db

    def get_by_id(self, property_id: int) -> Optional[Property]:
        return self.db.get(Property, property_id)

    def search(
        self,
        query: str = "",
        min_price: float | None = None,
        max_price: float | None = None,
        property_type: str = "",
        min_price_exclusive: bool = False,
        max_price_exclusive: bool = False,
    ) -> list[Property]:
        statement = select(Property)
        if query:
            search = f"%{query}%"
            statement = statement.where(
                (Property.title.ilike(search))
                | (Property.location.ilike(search))
                | (Property.description.ilike(search))
            )
        if min_price is not None:
            comparison = Property.price > min_price if min_price_exclusive else Property.price >= min_price
            statement = statement.where(comparison)
        if max_price is not None:
            comparison = Property.price < max_price if max_price_exclusive else Property.price <= max_price
            statement = statement.where(comparison)
        if property_type:
            statement = statement.where(Property.property_type == property_type)
        return self.db.exec(statement.order_by(Property.id.desc())).all()

    def list_for_owner(self, owner_id: int) -> list[Property]:
        return self.db.exec(
            select(Property).where(Property.owner_id == owner_id).order_by(Property.id.desc())
        ).all()
