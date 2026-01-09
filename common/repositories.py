from django.core.exceptions import ObjectDoesNotExist


class BaseRepository:
    """
    Base Repository with optional user scoping.

    Repository Pattern - abstracts data access layer.
    Supports user-scoped queries for models with 'user' field.

    Usage:
        # User-scoped (only that user's data):
        repo = OwnedGearRepository(user=request.user)

        # Global (all data, e.g., for admin):
        repo = BrandRepository()
    """

    model = None
    user_field = "user"

    def __init__(self, user=None):
        """
        Initialize repository with optional user.

        Args:
            user: User object to scope queries. If None, queries are global.
        """
        self.user = user

    def _get_base_queryset(self):
        """
        Get base queryset, optionally filtered by user.

        Returns:
            QuerySet filtered by user if user is set, otherwise all objects.
        """
        queryset = self.model.objects.all()

        if self.user and hasattr(self.model, self.user_field):
            # Filter by user if provided and model has user field
            filter_kwargs = {self.user_field: self.user}
            queryset = queryset.filter(**filter_kwargs)

        return queryset

    def get_all(self):
        return self._get_base_queryset()

    def get_by_id(self, obj_id):
        """
        Get single object by ID (for current user if set).

        Args:
            obj_id: Object ID

        Returns:
            Object instance or None if not found
        """
        try:
            return self._get_base_queryset().get(id=obj_id)
        except ObjectDoesNotExist:
            return None

    def create(self, **kwargs):
        """
        Create new object (auto-adds user if set).

        Args:
            **kwargs: Field values

        Returns:
            Created object instance
        """
        if (
            self.user
            and self.user_field not in kwargs
            and hasattr(self.model, self.user_field)
        ):
            kwargs[self.user_field] = self.user

        return self.model.objects.create(**kwargs)

    def update(self, obj_id, **kwargs):
        """
        Update object (only if belongs to user if user is set).

        Args:
            obj_id: Object ID
            **kwargs: Fields to update

        Returns:
            Updated object or None if not found
        """
        obj = self.get_by_id(obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
            return obj
        return None

    def delete(self, obj_id) -> bool:
        """
        Delete object (only if belongs to user if user is set).

        Args:
            obj_id: Object ID

        Returns:
            True if deleted, False if not found
        """
        obj = self.get_by_id(obj_id)
        if obj:
            obj.delete()
            return True
        return False

    def count(self):
        """
        Count objects (for current user if set).

        Returns:
            int: Number of objects
        """
        return self._get_base_queryset().count()

    def exists(self, **kwargs):
        """
        Check if object exists (for current user if set).

        Args:
            **kwargs: Filter criteria

        Returns:
            bool: True if exists
        """
        return self._get_base_queryset().filter(**kwargs).exists()
