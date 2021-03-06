from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json

# instantiate pusher
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)    
    items = room.itemNames()
    player.setStats()
    playerHealth = player.health
    playerAttack = player.attackPower
    playerDefense = player.defense
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'items':items, "health":playerHealth, 'attack':playerAttack, 'defense':playerDefense}, safe=True)



# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id    
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        items = nextRoom.itemNames()
        for p_uuid in currentPlayerUUIDs:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        for p_uuid in nextPlayerUUIDs:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'items':items, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        items = room.itemNames()
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'items':items, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    player = request.user.player
    player_id = player.id
    data = json.loads(request.body)    
    message = data['message']    
    room = player.room()
    players = room.playerUUIDs(player_id)
    for p_uuid in players:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} says \"{message}\"'})
    return JsonResponse({'name':player.user.username, 'message': message}, safe=True)

@csrf_exempt
@api_view(["POST"])
def grab(request):
    player = request.user.player
    player_id = player.id
    data = json.loads(request.body)    
    itemToGrab = data['item']    
    room = player.room()
    players = room.playerUUIDs(player_id)
    itemIDList = room.getItem(itemToGrab)      
    itemID = int(itemIDList) 
    if itemID is not None and itemID > 0:           
        item = Item.objects.get(id=itemID)
        itemName = item.title
        room.items.remove(item)
        player.inventory.add(item)
        for p_uuid in players:
                pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} grabs \"{itemName}\".'})
        return JsonResponse({'name':player.user.username, 'item': itemName}, safe=True)
    else:        
        return JsonResponse({'name':player.user.username, 'error':True}, safe=True)

@csrf_exempt
@api_view(["POST"])
def drop(request):
    player = request.user.player
    player_id = player.id
    data = json.loads(request.body)    
    itemToDrop = data['item']    
    room = player.room()
    players = room.playerUUIDs(player_id)
    itemIDList = player.getItem(itemToDrop)      
    itemID = int(itemIDList) 
    if itemID is not None and itemID > 0:           
        item = Item.objects.get(id=itemID)
        itemName = item.title
        player.inventory.remove(item)
        room.items.add(item)
        for p_uuid in players:
                pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} drops \"{itemName}\".'})
        return JsonResponse({'name':player.user.username, 'item': itemName}, safe=True)
    else:        
        return JsonResponse({'name':player.user.username, 'error':True}, safe=True)

@csrf_exempt
@api_view(["GET"])
def inventory(request):
    player = request.user.player 
    items = player.itemNames()
    equippedWeaponName = "Empty"
    equippedWeaponID = player.equippedWeapon   
    equippedArmorName = "Empty"
    equippedArmorID = player.equippedArmor 
    try:
        equippedWeapon = Weapon.objects.get(id=equippedWeaponID)
        equippedWeaponName = equippedWeapon.title
    except:
        pass
    try:
        equippedArmor = Armor.objects.get(id=equippedArmorID)
        equippedArmorName = equippedArmor.title
    except:
        pass
    return JsonResponse({'items':items, "equippedWeapon":equippedWeaponName, "equippedArmor":equippedArmorName}, safe=True)   

@csrf_exempt
@api_view(["POST"])
def equip(request):
    player = request.user.player
    data = json.loads(request.body)
    itemToEquip = data['item']
    itemIDList = player.getItem(itemToEquip)      
    itemID = int(itemIDList)
    try:
        itemIDList = player.getItem(itemToEquip)      
        itemID = int(itemIDList) 
    except:
        itemID = None
    if itemID is not None and itemID > 0:           
        item = None        
        try:
            item = Armor.objects.get(id=itemID) 
        except:
            pass
        try:
            item = Weapon.objects.get(id=itemID)
        except:
            pass
        finally:
            if item is None:
                return JsonResponse({'error':True, 'err_message': 'That item is can not be equipped.'}, safe=True)  
        itemName = item.title
        if item.isWeapon:   
            if player.equippedWeapon == 0:
                player.inventory.remove(item)
                player.equippedWeapon=itemID
                player.save()
                player.setStats()
                return JsonResponse({'item':itemName}, safe=True)
            else:
                return JsonResponse({'error':True, 'err_message': 'You already have a weapon equipped.'}, safe=True)
        elif item.isArmor:
            if player.equippedArmor == 0:
                player.inventory.remove(item)
                player.equippedArmor=itemID
                player.save()
                player.setStats()
                return JsonResponse({'item':itemName}, safe=True)
            else:
                return JsonResponse({'error':True, 'err_message': 'You already have armor equipped.'}, safe=True)
    else:
        return JsonResponse({'error':True, 'err_message': 'That item does not exist in this world.'}, safe=True)



@csrf_exempt
@api_view(["POST"])
def takeOffItem(request):    
    player = request.user.player
    data = json.loads(request.body)    
    itemToUnequip = data['item']    
    try:
        itemIDList = Item.objects.get(title=itemToUnequip)       
        itemID = itemIDList.id  
    except:
        itemID = None
    if itemID is not None and itemID > 0:   
        item = None        
        try:
            item = Armor.objects.get(id=itemID) 
        except:
            pass
        try:
            item = Weapon.objects.get(id=itemID)
        except:
            pass
        finally:
            if item is None:
                return JsonResponse({'error':True, 'err_message': 'That item is should not have been equipped.'}, safe=True)                
        itemName = item.title        
        if item.isWeapon:
            if itemID == player.equippedWeapon:
                player.inventory.add(item)
                player.equippedWeapon = 0    
                player.save()       
                player.setStats()     
                return JsonResponse({'item':itemName}, safe=True)
            else:
                return JsonResponse({'error':True, 'err_message': 'That item is not equipped.'}, safe=True)
        elif item.isArmor:
            if itemID == player.equippedArmor:
                player.inventory.add(item)
                player.equippedArmor = 0
                player.save()
                player.setStats()
                return JsonResponse({'item':itemName}, safe=True)
            else:
                return JsonResponse({'error':True, 'err_message': 'That item is not equipped.'}, safe=True)        
    else:
        return JsonResponse({'error':True, 'err_message': 'That item does not exist in this world.'}, safe=True)

@csrf_exempt
@api_view(["GET"])
def getStats(request): 
    user = request.user
    player = user.player
    player.setStats()
    playerHealth = player.health
    playerAttack = player.attackPower
    playerDefense = player.defense
    return JsonResponse({"health":playerHealth, 'attack':playerAttack, 'defense':playerDefense}, safe=True)
