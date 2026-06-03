from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from offers.models import PromotionalOffer

@receiver([post_save, post_delete], sender=PromotionalOffer)
def clear_offers_cache(sender, **kwargs):
    cache.delete("active_promotional_offers")
