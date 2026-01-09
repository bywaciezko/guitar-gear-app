from django.db.models import Q, QuerySet
from common.repositories import BaseRepository
from equipment.models import OwnedGear

"""
QuerySet:
We aren't fetching data every time
instead, we're building a query that will only be evaluated when the data
is actually accessed (e.g., in a loop, list, or template).
"""


class OwnedGearRepository(BaseRepository):
    model = OwnedGear

    def filter_gear(
        self,
        gear_types=None,
        brand_id=None,
        search_query=None,
        favorites_only=False,
    ) -> QuerySet:
        """
        Universal filter method for gear with multiple criteria.
        Automatically scoped to self.user

        Args:
            gear_types: list of types ['guitar', 'amplifier'] or None (all)
            brand_id: int or None
            search_query: str or None
            favorites_only: bool
        """
        queryset = self._get_base_queryset()

        if gear_types:
            type_filters = Q()

            if "guitar" in gear_types:
                type_filters |= Q(guitar__isnull=False)
            if "amplifier" in gear_types:
                type_filters |= Q(amplifier__isnull=False)
            if "pedal" in gear_types:
                type_filters |= Q(pedal__isnull=False)

            queryset = queryset.filter(type_filters)

        if brand_id:
            queryset = queryset.filter(
                Q(guitar__brand_id=brand_id)
                | Q(amplifier__brand_id=brand_id)
                | Q(pedal__brand_id=brand_id)
            )

        if search_query:
            queryset = queryset.filter(
                Q(nickname__icontains=search_query)
                | Q(guitar__name__icontains=search_query)
                | Q(amplifier__name__icontains=search_query)
                | Q(pedal__name__icontains=search_query)
            )

        if favorites_only:
            queryset = queryset.filter(is_favorite=True)

        queryset = queryset.select_related(
            "guitar",
            "guitar__brand",
            "amplifier",
            "amplifier__brand",
            "pedal",
            "pedal__brand",
        )

        return queryset.order_by("is_favorite", "-created_at")

    def get_favorites() -> QuerySet:
        return self.filter_gear(favorites_only=True)

    def count_by_type(self) -> dict[str, int]:
        base_qs = self._get_base_queryset()
        return {
            "guitars": base_qs.filter(guitar__isnull=False).count(),
            "amplifiers": base_qs.filter(amplifier__isnull=False).count(),
            "pedals": base_qs.filter(pedal__isnull=False).count(),
        }
