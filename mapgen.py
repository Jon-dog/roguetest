from firstrl import *
from main import *

def is_blocked(x, y):
    # first test the map tile
    if map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False


def create_room(room):
    global map
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False


def create_h_tunnel(x1, x2, y):
    global map
    # horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global map
    # vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def random_choice_index(chances):  # choose one option from list of chances, returning its index
    # the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1


def random_choice(chances_dict):
    # choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]


def from_dungeon_level(table):
    # returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


def place_objects(room):
    # this is where we decide the chance of each monster or item appearing.

    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

    #chance of each monster
    monster_chances = {}
    monster_chances['skeleton'] = 80  # skeleton always shows up, even if all other monsters have 0 chance
    monster_chances['demon'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])

    #maximum number of items per room
    max_items = from_dungeon_level([[1, 2], [2, 4]])

    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['heal'] = 35  # healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] = from_dungeon_level([[25, 6]])
    item_chances['confuse'] = from_dungeon_level([[10, 2]])
    item_chances['combknife'] = from_dungeon_level([[5, 4]])
    item_chances['shield'] = from_dungeon_level([[15, 8]])

    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'skeleton':
                #create an skeleton
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35,
                                                    death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 's', 'skeleton', libtcod.dark_gray, blocks=True,
                                         fighter=fighter_component, ai=ai_component)

            elif choice == 'demon':
                #create a demon
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100,
                                                    death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 'D', 'demon', libtcod.darker_red,
                                         blocks=True, fighter=fighter_component, ai=ai_component)

            objects.append(monster)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                #create a healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'bandages', libtcod.violet, item=item_component)

            # elif choice == 'lightning':
            #     #create a lightning bolt scroll
            #     item_component = Item(use_function=cast_lightning)
            #     item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)

            elif choice == 'fireball':
                #create a fireball scroll
                item_component = Item(use_function=cast_explosive)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

            elif choice == 'confuse':
                #create a confuse scroll
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

            elif choice == 'combknife':
                #create a sword
                equipment_component = Equipment(slot='right hand', power_bonus=3)
                item = Object(x, y, '/', 'combat knife', libtcod.sky, equipment=equipment_component)

            elif choice == 'shield':
                #create a shield
                equipment_component = Equipment(slot='left hand', defense_bonus=1)
                item = Object(x, y, '[', 'riot shield', libtcod.darker_orange, equipment=equipment_component)

            objects.append(item)
            item.send_to_back()  # items appear below other objects
            item.always_visible = True  # items are visible even out-of-FOV, if in an explored area