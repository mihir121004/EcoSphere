from django.db.models import Sum
from store.models import CartItem


def cart_context(request):
    """Makes the live cart item count available on every page."""
    count = 0
    if request.user.is_authenticated:
        count = CartItem.objects.filter(
            cart__user=request.user
        ).aggregate(total=Sum('quantity'))['total'] or 0
    return {'cart_item_count': count}
