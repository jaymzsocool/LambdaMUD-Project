from django.contrib.auth.models import User
from adventure.models import Player, Room, Item, Weapon


Room.objects.all().delete()

r_outside = Room(title="Outside Cave Entrance",
               description="North of you, the cave mount beckons")

r_foyer = Room(title="Foyer", description="""Dim light filters in from the south. Dusty
passages run north and east.""")

r_overlook = Room(title="Grand Overlook", description="""A steep cliff appears before you, falling
into the darkness. Ahead to the north, a light flickers in
the distance, but there is no way across the chasm.""")

r_narrow = Room(title="Narrow Passage", description="""The narrow passage bends here from west
to north. The smell of gold permeates the air.""")

r_treasure = Room(title="Treasure Chamber", description="""You've found the long-lost treasure
chamber! Sadly, it has already been completely emptied by
earlier adventurers. The only exit is to the south.""")


r_outside.save()
r_foyer.save()
r_overlook.save()
r_narrow.save()
r_treasure.save()

i_rock = Item(title="Rock", description="A rock that fit in the palm of your hand.")
i_rock.save()

w_sword = Weapon(title="Sword", description="A standard one handed arming sword.", itemAttackValue= 5)
w_sword.save()

r_outside.items.add(i_rock)
r_outside.items.add(w_sword)
r_foyer.items.add(w_sword)
r_overlook.items.add(w_sword)
r_narrow.items.add(w_sword)
r_treasure.items.add(w_sword)

# Link rooms together
r_outside.connectRooms(r_foyer, "n")
r_foyer.connectRooms(r_outside, "s")

r_foyer.connectRooms(r_overlook, "n")
r_overlook.connectRooms(r_foyer, "s")

r_foyer.connectRooms(r_narrow, "e")
r_narrow.connectRooms(r_foyer, "w")

r_narrow.connectRooms(r_treasure, "n")
r_treasure.connectRooms(r_narrow, "s")


players=Player.objects.all()
for p in players:
  p.currentRoom=r_outside.id
  p.save()

