from django.core.management.base import BaseCommand
from ...models import Vessel
import threading
from django.db import transaction

class Command(BaseCommand):
    help = "Simulate condition when withdrawing refrigerant from a vessel."

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            Vessel.objects.all().delete()
            vessel = Vessel.objects.create(name="Test Vessel", content=50.0)

        self.stdout.write("Simulating condition...")
        self.run_simulation(vessel.id)

    def run_simulation(self, vessel_id):
        barrier = threading.Barrier(2)

        def user1():
            barrier.wait()
            self.withdraw_safe(vessel_id)

        def user2():
            barrier.wait()
            self.withdraw_safe(vessel_id)

        t1 = threading.Thread(target=user1)
        t2 = threading.Thread(target=user2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        vessel = Vessel.objects.get(id=vessel_id)
        self.stdout.write(f"Remaining content: {vessel.content} kg")

    def withdraw_safe(self, vessel_id):
        with transaction.atomic():
            vessel = Vessel.objects.select_for_update().get(id=vessel_id)
            vessel.content -= 10.0
            vessel.save()
