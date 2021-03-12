"""
Simple 2d world where the player can interact with the items in the world.
"""

__author__ = "Xiaoyu Dong"
__date__ = "10.10.2019"
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

import sys
import time

from PIL import Image
from typing import Tuple, List

import pymunk

from game.block import Block, MysteryBlock
from game.entity import Entity, BoundaryWall
from game.mob import Mob, CloudMob, Fireball
from game.item import DroppedItem, Coin
from game.view import GameView, ViewRenderer
from game.world import World
from tkinter import simpledialog
from game.util import *
from tkinter import filedialog

from level import load_world, WorldBuilder
from player import Player

BLOCK_SIZE = 2 ** 4
MAX_WINDOW_SIZE = (1080, math.inf)

GOAL_SIZES = {
    "flag": (0.2, 9),
    "tunnel": (2, 2)
}

BLOCKS = {
    '#': 'brick',
    '%': 'brick_base',
    '?': 'mystery_empty',
    '$': 'mystery_coin',
    '^': 'cube',
    'b': 'bounce',
    "I": "goal",
    "=":"tunnel",
    "S" :"switch"



}

ITEMS = {
    'C': 'coin',
    '*': 'star'
}

MOBS = {
    '&': "cloud",
    '@': "mushroom",
    '6':"koopa"
}


def create_block(world: World, block_id: str, x: int, y: int, *args):
    """Create a new block instance and add it to the world based on the block_id.

    Parameters:
        world (World): The world where the block should be added to.
        block_id (str): The block identifier of the block to create.
        x (int): The x coordinate of the block.
        y (int): The y coordinate of the block.
    """
    block_id = BLOCKS[block_id]
    if block_id == "mystery_empty":
        block = MysteryBlock()
    elif block_id == "mystery_coin":
        block = MysteryBlock(drop="coin", drop_range=(3, 6))
    elif block_id=="bounce":
        block=Bounce()
    elif block_id=="goal":
        #create goal as a new block
        block=Goal()
    elif block_id=="tunnel":
        #create tunnel as a new block
        block=Tunnel()
    elif block_id == "switch":
        #create switch as a new block
        block = Switch()

    else:
        block = Block(block_id)

    world.add_block(block, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_item(world: World, item_id: str, x: int, y: int, *args):
    """Create a new item instance and add it to the world based on the item_id.

    Parameters:
        world (World): The world where the item should be added to.
        item_id (str): The item identifier of the item to create.
        x (int): The x coordinate of the item.
        y (int): The y coordinate of the item.
    """
    item_id = ITEMS[item_id]
    if item_id == "coin":
        item = Coin()
    elif item_id == "star":
        #create star as a new item
        item = Star()

    else:
        item = DroppedItem(item_id)

    world.add_item(item, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_mob(world: World, mob_id: str, x: int, y: int, *args):
    """Create a new mob instance and add it to the world based on the mob_id.

    Parameters:
        world (World): The world where the mob should be added to.
        mob_id (str): The mob identifier of the mob to create.
        x (int): The x coordinate of the mob.
        y (int): The y coordinate of the mob.
    """
    mob_id = MOBS[mob_id]
    if mob_id == "cloud":
        mob = CloudMob()
    elif mob_id == "fireball":
        mob = Fireball()
    elif mob_id=="mushroom":
        #Create a new mob instance(mushroom) and add it to the world based on the mob_id
        mob= Mushroom()
    elif mob_id=="koopa":
        mob=Koopa()

    else:
        mob = Mob(mob_id, size=(1, 1))

    world.add_mob(mob, x * BLOCK_SIZE, y * BLOCK_SIZE)




def create_unknown(world: World, entity_id: str, x: int, y: int, *args):
    """Create an unknown entity."""
    world.add_thing(Entity(), x * BLOCK_SIZE, y * BLOCK_SIZE,
                    size=(BLOCK_SIZE, BLOCK_SIZE))









BLOCK_IMAGES = {
    "brick": "brick",
    "brick_base": "brick_base",
    "cube": "cube",
    "bounce":"bounce_block",
    "goal":"flag",
    "tunnel":"tunnel",
    "switch":"switch"


}

ITEM_IMAGES = {
    "coin": "coin_item",
    "star":"star"
}

MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down",
    "mushroom":"mushroom",
    "koopa":"koopa"
}


class SpriteSheetLoader():
    "Load an image in the file location of images/{file}.png"
    def __init__(self):
        self._images = {}

    def load_image(self,filename, image_name, x1, y1, x2, y2, flipped):
        if flipped == False:
            sheet = Image.open(filename)
            image = sheet.crop((x1, y1, x2, y2))
        if flipped == True:
            sheet = Image.open(filename)
            image = sheet.crop((x1, y1, x2, y2)).transpose(Image.FLIP_LEFT_RIGHT)

        self._images[image_name] = ImageTk.PhotoImage(image)
        return self._images







class Config():
    """
    a class of config which is configuration of the game, eg: mass, health, max_velocity
    """
    def __init__(self):                                
        """
        Construct a dictionary(config) which store configuration of the game
        """
        self._config={}

    def make_config_dic(self,filename):
        """
        Parameters: filename(str),for instance:"config.txt"
        When the game is launched the user enter the file path for a configuration file.
        return:a dictionary(config) which store configuration of the game. it is a nested dictionary
        """
        try:
            with open(filename, "r") as f:
                for line in f:
                    line=line.strip()
                    if line.startswith("==") and line.endswith("=="):
                        heading=line[2:-2]
                        self._config[heading]={}
                    else:
                        attr,_,value=line.partition(":")
                        attr=attr.strip()
                        value=value.strip()
                        self._config[heading][attr]=value
        except FileNotFoundError:
            print("File does not exist")
        #return self._config

    def get_value(self,setting):
        """
        get value of gravity or character or mass and other configuration
        parameter: setting(str): for instance: 'World,gravity' , "Player,character"
        return: value of the right side key(gravity,character,etc) of nested config dictionary
        """
        heading,_,attr=setting.partition(',')
        return self._config[heading][attr]

    def limited_velocity(self,velocity):
        """

        :param velocity(str):it is 'Player,max_velocity', used in move funtion
        :return:max_velocity(str) (max velocity of x)
        """
        max_velocity = int(self._config.get_value(velocity))
        return max_velocity


class Highscores():
    """
    store the high scores for each level in a file.
    The highscore information is stored in (a) txt file(s).
    high scores bar only display the top ten entries in the window. If
    when the file doesn't exist, print("File does not exist")
    """
    def __init__(self):
        self._database = {}
        # initialize name and score, which will be used in for loop

    def sort_list(self,filename):
        """
        :param filename(str): for examply:"scores level1.txt"
        :return:self._database_sorted10(dict)
        """
        try:
            with open(filename, 'r') as reader:
                # readlines：make each line of file (include"\n")into list
                lines = reader.readlines()
                # dictionary database
                # key:name -> value:score

                name = ""
                score = 0
                for line in lines:
                    # dont read \n
                    if line == '\n':
                        continue
                    elif line.startswith("name"):
                        part1, _, part2 = line.partition(",")
                        name = part1.split(":")[1].strip()

                        score = int(part2.split(":")[1].strip())
                    # save name and score in dictionary as key and value
                    self._database[name] = score
                    self._database_sorted = sorted(self._database.items(), key=lambda item: -item[1])
                    self._database_sorted10=self._database_sorted[0:10]
                return self._database_sorted10
        except FileNotFoundError:
            print("File does not exist")



class Koopa(Mob):
    """
    an enemy who can kill player's health(-2)
    """
    _id="koopa"
    def __init__(self):
        super().__init__(self._id, size=(16, 16), weight=150, tempo=-110)
        self._koopasquished = False

    def step(self, time_delta, game_data):
        super().step(time_delta, game_data)

    def on_hit(self, event: pymunk.Arbiter, data):
        world, player = data
        # self._player = player
        player_velocity = player.get_velocity()
        direction = get_collision_direction(player, self)
        # when mushroom be steped by player,player will be bounce a little bit
        if direction == ABOVE:
            self._koopasquished = True
            world.remove_mob(self)
            x_velocity = player_velocity[0]
            player.set_velocity((x_velocity, -200))
            player.set_bigger(True)


        else:
            # player meet with mushroom in L or R
            player.change_health(-2)
            y_velocity = player_velocity[1]
            # mushroom opposite his direction
            self.set_tempo(-self.get_tempo())

            if direction == 'L':
                player.set_velocity((-110, y_velocity))
            else:
                player.set_velocity((110, y_velocity))

    def is_koopasquished(self):
        return self._koopasquished




class Switch(Block):
    """
    When a player lands on-top of a switch, all bricks within a close radius of the switch disappear. A player
    cannot trigger the switch by walking into the side of it (the player stops moving as if it were any other block)
    """
    _id = "switch"
    _switch_status: bool = False
    _switch_time1=None

    def __init__(self):
        super().__init__()
        #inherite parent class of block


    def get_switch_status(self):
        return self._switch_status

    def on_hit(self, event, data):
        """
         When a player lands on-top of a switch, all bricks within a close radius of the switch disappear. A player
         cannot trigger the switch by walking into the side of it (the player stops moving as if it were any other block)
        Parameters:
            event (pymunk.Arbiter): Details on the collision event.
            data (tuple<World, Player): Useful data to use to process the collision.
        """
        world, player = data
        #player and world input into this function, thus we can use world's function
        if get_collision_direction(player, self) == "A":
            #when player collision the top of the switch, it status become True. otherwise it is False
            self._switch_status = True
            self._switch_time1 = time.time()
            x, y = self.get_position()
            #get_position()  Returns the (x, y) position of the block's centre

            all_entity = world.get_things_in_range(x, y, 80)
            #all entities within a radius of the switch

            self._all_brick_position_list = []
            for n in all_entity:
                if str(n) == "Block(brick)":
                    self._all_brick_position_list.append(n.get_position())
                    world.remove_thing(n)


    def recall_bricks(self,data):
        """
        make disappeared brick back
        :param data: (tuple<World, Player>): Useful data to use to process the collision.

        """
        world, player = data
        for m in self._all_brick_position_list:
            x, y = m
            world.add_block(Block("brick"),x, y)
        #a function to recreate all the bricks after 10 seconds has passed


class Mushroom(Mob):
    _id="mushroom"

    def __init__(self):
        super().__init__(self._id, size=(16, 16), weight=220, tempo=-40)
        # mushroom moves at a reasonably slow rate
        self._squished=False

    def step(self, time_delta, game_data):
        super().step(time_delta, game_data)
        #inherit

    def on_hit(self, event: pymunk.Arbiter, data):
        world, player = data
        #self._player = player
        self._start=0
        player_velocity = player.get_velocity()
        direction=get_collision_direction(player,self)
        #self._master=master
        #when mushroom be steped by player,player will be bounce a little bit
        if direction==ABOVE:
            self._squished = True
            player.set_mushroom_2s(True)
            if player.is_2s()==True:
                if time.time()-self._start>3:
                    world.remove_mob(self)
                    player.set_mushroom_2s(False)


            x_velocity = player_velocity[0]
            player.set_velocity((x_velocity, -200))

        else:
            #player meet with mushroom in L or R,lose health(-1)
            player.change_health(-1)
            y_velocity = player_velocity[1]
            #mushroom opposite his direction
            self.set_tempo(-self.get_tempo())

            if direction == 'L':
                player.set_velocity((-90,y_velocity))
            else:
                player.set_velocity((90,y_velocity))

    def is_squished(self):
        #after step on the mushroom squished animation
        return self._squished

class Star(DroppedItem):
    """
    star is dropped item, that makes the player invincible for 10 seconds
    """

    _id="star"
    def __init__(self, time:int= 0):
        super().__init__()


    def collect(self, player:Player):
        """collect star"""
        invincible=True
        player.set_invincible(invincible)
        #Any mobs that the player collides with during invincible time should be immediately destroyed.





class Goal(Block):
    """
     when a player collides with flagpole of the goal player has max health
     goal allows player change between levels and record their name into highscores list.
    """
    _id = "goal"
    _cell_size=(2,9)


    def __init__(self):
        super().__init__()
        #inherit parent (Block)




class Tunnel(Block):
    """
    when player presses the down key while standing on top of this block, the player go to another level.
    """
    _id = "tunnel"
    _cell_size = (2, 2)

    def __init__(self):
        super().__init__()
        #inherit parent (Block)



class Bounce(Block):
    """
    a type of block which propels the player into the air when they walk over or jump on top of the block
    """

    _id="bounce"
    def __init__(self):
        super().__init__()
        self._anime = False
    def is_anime(self):
        #used to determin whether need animation
        return self._anime
    def on_hit(self,event,data):
        """

        :param event:
        :param data: world, player
        describe what happen after hit on bounce
        """
        world, player=data
        self._player= player
        if get_collision_direction(player,self) != "A":
            return
        else:
            #make bounce has animation
            self._anime = True
            player_velocity = self._player.get_velocity()
            x_velocity = player_velocity[0]
            self._player.set_velocity((x_velocity, -310))


class MarioViewRenderer(ViewRenderer):
    """A customised view renderer for a game of mario."""

    @ViewRenderer.draw.register(Player)

    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:

        if instance.get_name()=="luigi":
            if shape.body.velocity.x >= 0:
                image = self.load_image("luigi_right")
            else:
                image = self.load_image("luigi_left")

        if instance.get_name()=="Mario":
            if shape.body.velocity.x >= 0:
                image = self.load_image("mario_right")
            else:
                image = self.load_image("mario_left")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]

    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Switch)
    #new image after switch is steped on
    def _draw_mystery_block(self, instance: Switch, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance._switch_status:
            image = self.load_image("switch_pressed")
        else:
            image = self.load_image("switch")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]



class AnimationMario(ViewRenderer):
    """A further customised aniation view renderer for a game of mario."""

    def __init__(self, BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES):
        super().__init__(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)
        self._coin_sprite_count = 0
        self._player_sprite_count = 0
        self._bounce_sprite_count = 0
        self._mushroom_sprite_count = 0
        self._koopa_sprite_count =0


        #load image into spritesheetloader._images(a dictionary)
        self._spritesheetloader = SpriteSheetLoader()

        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_walk2", 97, 35, 112, 50, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_walk3", 114, 35, 130, 50, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_walk4", 131, 35, 146, 50, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_leftwalk2", 97, 35, 112, 50, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_leftwalk3", 114, 35, 130, 50, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_leftwalk4", 131, 35, 146, 50, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_jump", 165, 34, 180, 50, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_leftjump", 165, 34, 180, 50, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_m_fail", 182, 34, 197, 50, False)

        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_walk2", 97, 100, 112, 114, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_walk3", 114, 100, 130, 114, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_walk4", 131, 100, 146, 114, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_leftwalk2", 97, 100, 112, 114, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_leftwalk3", 114, 100, 130, 114, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_leftwalk4", 131, 100, 146, 114, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_jump", 165, 99, 180, 114, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_leftjump",  165, 99, 180, 114, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "img_l_fail", 182, 99, 197, 114, False)

        self._spritesheetloader.load_image("spritesheets/characters.png", "big_m_r",80, 1, 95, 32, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "big_m_l", 80, 1, 95, 32, True)
        self._spritesheetloader.load_image("spritesheets/characters.png", "big_l_r", 80, 66, 95, 97, False)
        self._spritesheetloader.load_image("spritesheets/characters.png", "big_l_l", 80, 66, 95, 97, True)

        self._spritesheetloader.load_image("spritesheets/items.png", "img_coin1", 2, 98, 13, 111, False)
        self._spritesheetloader.load_image("spritesheets/items.png", "img_coin2", 19, 113, 27, 126, False)
        self._spritesheetloader.load_image("spritesheets/items.png", "img_coin3", 37, 113, 42, 126, False)
        self._spritesheetloader.load_image("spritesheets/items.png", "img_coin4", 55, 113, 57, 126, False)

        self._spritesheetloader.load_image("spritesheets/enemies.png", "mush_squished", 33, 24, 47, 31, False)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "mush_walk1", 0, 16, 15, 31, False)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "mush_leftwalk", 0, 16, 15, 31, True)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_squished", 33, 24, 47, 32, False)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_R", 96, 9, 111, 32, True)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_walk1", 112, 10, 127, 32, False)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_R_walk", 112, 10, 127, 32, True)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_angelwalk1", 144, 9, 160, 32, False)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_angelR_walk", 144, 9, 160, 32, True)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_angelwalk2", 128, 8, 143, 32, False)
        self._spritesheetloader.load_image("spritesheets/enemies.png", "koopa_angelR_walk2", 128, 8, 143, 32, True)

        self._spritesheetloader.load_image("spritesheets/items.png", "bounceblock1", 254, 48, 270, 63, False)
        self._spritesheetloader.load_image("spritesheets/items.png", "bounceblock2", 240, 40, 256, 63, False)
        self._spritesheetloader.load_image("spritesheets/items.png", "bounceblock3", 224, 33, 240, 63, False)
        #make this dictionary(spritesheetloader._images) can be used in MarioApp
        self._images=self._spritesheetloader._images

    @ViewRenderer.draw.register(Coin)
    def _draw_coin_item(self, instance: Coin, shape: pymunk.Shape,
                        view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        # make animation :coin shinning, using image from "spritesheets/items.png"
        self._coin_sprite_count += 1
        if self._coin_sprite_count<5:
            image = self.load_image("img_coin1")
        elif self._coin_sprite_count<10:
            image = self.load_image("img_coin2")
        elif self._coin_sprite_count <15:
            image = self.load_image("img_coin3")
        else:
            image = self.load_image("img_coin4")
            self._coin_sprite_count =0

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                      image=image, tags="item")]



    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        #When the player is walking, jumping or falling animate the player with sprites images.
        if instance.get_name() == "luigi":
            if instance.is_bigger()==True:
                if shape.body.velocity.x >= 0:
                    image = self.load_image("big_l_r")
                else:
                    image = self.load_image("big_l_l")
            else:

                if shape.body.velocity.y < 0:
                    image = self.load_image("img_l_jump")
                elif shape.body.velocity.y > 0:
                    image = self.load_image("img_l_fail")
                elif shape.body.velocity.x == 0:
                    image = self.load_image("luigi_right")
                else:
                    self._player_sprite_count += 1
                    if shape.body.velocity.x > 0:
                        if self._player_sprite_count <5:
                            image = self.load_image("luigi_right")
                        elif self._player_sprite_count<10:
                            image = self.load_image("img_l_walk2")
                        elif self._player_sprite_count <15:
                            image = self.load_image("img_l_walk3")
                        else:
                            image = self.load_image("img_l_walk4")
                            self._player_sprite_count = 0
                    else:
                        if self._player_sprite_count< 5:
                            image = self.load_image("luigi_left")
                        elif self._player_sprite_count< 10:
                            image = self.load_image("img_l_leftwalk2")
                        elif self._player_sprite_count< 15:
                            image = self.load_image("img_l_leftwalk3")
                        else:
                            image = self.load_image("img_l_leftwalk4")
                            self._player_sprite_count = 0



        if instance.get_name() == "Mario":
            if instance.is_bigger()==True:
                if shape.body.velocity.x >= 0:
                    image = self.load_image("big_m_r")
                else:
                    image = self.load_image("big_m_l")
            else:
                if shape.body.velocity.y < 0:
                    image = self.load_image("img_m_jump")
                elif shape.body.velocity.y > 0:
                    image = self.load_image("img_m_fail")
                elif shape.body.velocity.x == 0:
                    image = self.load_image("mario_right")
                else:
                    self._player_sprite_count += 1
                    if shape.body.velocity.x > 0:
                        if self._player_sprite_count <5:
                            image = self.load_image("mario_right")
                        elif self._player_sprite_count<10:
                            image = self.load_image("img_m_walk2")
                        elif self._player_sprite_count <15:
                            image = self.load_image("img_m_walk3")
                        else:
                            image = self.load_image("img_m_walk4")
                            self._player_sprite_count = 0
                    elif shape.body.velocity.x < 0:
                        if self._player_sprite_count< 5:
                            image = self.load_image("mario_left")
                        elif self._player_sprite_count< 10:
                            image = self.load_image("img_m_leftwalk2")
                        elif self._player_sprite_count< 15:
                            image = self.load_image("img_m_leftwalk3")
                        else:
                            image = self.load_image("img_m_leftwalk4")
                            self._player_sprite_count = 0


        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]



    @ViewRenderer.draw.register(Bounce)
    def _draw_bounce_block(self, instance: Bounce, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        #When the bounce block is used, animate the extension of the bounce block using the sprites images.
        self._bounce_sprite_count+=1
        if instance.is_anime()== False:
            image = self.load_image("bounceblock1")
            self._bounce_sprite_count = 0
        elif instance.is_anime()== True:
            if self._bounce_sprite_count<2:
                image = self.load_image("bounceblock2")
            elif self._bounce_sprite_count<4:
                image = self.load_image("bounceblock3")
            elif self._bounce_sprite_count<6:
                image = self.load_image("bounceblock2")
            else:
                image = self.load_image("bounceblock1")
                self._bounce_sprite_count = 0

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]


    @ViewRenderer.draw.register(Mushroom)
    def _draw_mushroom_item(self, instance:Mushroom, shape: pymunk.Shape,
                        view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        # When the mushroom mob is walking, animate the walk using images from "spritesheets/enemies.png".

        if instance.is_squished()==True:
            image=self.load_image("mush_squished")
        else:
            self._mushroom_sprite_count += 1
            if self._mushroom_sprite_count<5:
                image = self.load_image("mush_walk1")
            elif self._mushroom_sprite_count<10:
                image = self.load_image("mush_leftwalk")
            elif self._mushroom_sprite_count <15:
                image = self.load_image("mush_walk1")
            else:
                image = self.load_image("mush_leftwalk")
                self._mushroom_sprite_count =0

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                      image=image, tags="mob")]

    #animation of new mob koopa
    @ViewRenderer.draw.register(Koopa)
    def _draw_mushroom_item(self, instance:Koopa, shape: pymunk.Shape,
                        view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_koopasquished()==True:
            image=self.load_image("koopa_squished")
        else:
            self._koopa_sprite_count +=1
            x,y=instance.get_velocity()
            if x >= 0:
                if x==0:
                    image = self.load_image("koopa_R")
                elif self._koopa_sprite_count < 2:
                    image = self.load_image("koopa_R_walk")
                elif self._koopa_sprite_count < 4:
                    image = self.load_image("koopa_R")
                elif self._koopa_sprite_count < 6:
                    image = self.load_image("koopa_R_walk")
                elif self._koopa_sprite_count < 8:
                    image = self.load_image("koopa_R")
                    self._koopa_sprite_count = 0
            elif x<0:
                if self._koopa_sprite_count < 3:
                    image = self.load_image("koopa")
                else:
                    image = self.load_image("koopa_walk1")
                    self._koopa_sprite_count = 0

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                      image=image, tags="mob")]








class StatusDisplay(tk.Frame):
    """display current scores and health bar """
    def __init__(self, master,player, size):
        # inherit parent window
        super().__init__(master)
        self._player = player
        width, height = size
        self._maxWidth = width
        #use self ,means this instance
        self._bar=tk.Canvas(master,width = width, height = 20)
        self._bar.pack()
        #current scores bar
        self._label = tk.Label(master, text="Score: 0")
        self._label.pack(side=tk.BOTTOM)
        self.change()
        self._player.on_hit=self.change

    def change(self):
        """
        a function which can change player's health value and make the health bar changes
        :return:
        """
        max_health = self._player.get_max_health()
        current_health = self._player.get_health()
        health_percentage = current_health/max_health
        #delete all healthbar
        self._bar.delete(self._bar.find_all())
        #all become black
        self._bar.create_rectangle(0, 0, self._maxWidth, 20, fill="black")

        if self._player.is_invincible() == True:
            color = "yellow"
        else:
            if health_percentage >= 0.5:
                color="green"
            elif health_percentage < 0.5 and health_percentage >= 0.25:
                color="orange"
            else:
                color = "red"

        #according to percentage use different color create rectangle
        self._bar.create_rectangle(0,0,self._maxWidth*health_percentage,20,fill=color)
        #update scores
        self._label.config(text="Scores:{0}".format(self._player.get_score()))




class MarioApp:
    """High-level app class for Mario, a 2d platformer"""


    _world: World

    def __init__(self, master: tk.Tk):
        """Construct a new game of a MarioApp game.

        Parameters:
            master (tk.Tk): tkinter root widget
        """

        master.update_idletasks()
        #object of config
        self._config = Config()
        filename = filedialog.askopenfilename()
        self._config.make_config_dic(filename)
        # When the game is launched the user should be prompted to enter the file path for a configuration file.

        self._database= Highscores()
        self._master = master
        self._start=0
        self._switch_time1 =0
        self._actived_switch = None

        #read config
        y_gravity=int(self._config.get_value('World,gravity'))
        world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, y_gravity), fallback=create_unknown)
        world_builder.register_builders(BLOCKS.keys(), create_block)
        world_builder.register_builders(ITEMS.keys(), create_item)
        world_builder.register_builders(MOBS.keys(), create_mob)
        self._builder = world_builder
        #read config
        max_velocity=int(self._config.get_value('Player,max_velocity'))

        #read config
        starting_health = int(self._config.get_value('Player,health'))
        self._max_health = starting_health
        #save the object of Player
        self._player = Player(name=self._config.get_value("Player,character"), max_health=starting_health)


        #at first current level is read from confif, then modify it in load method
        self._current_level = self._config.get_value('World,start')
        self.reset_world(self._current_level)

        #self._renderer = MarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)
        self._renderer = AnimationMario(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)

        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        self._view = GameView(master, size, self._renderer)
        self._view.pack()
        self.bind()


        #default invincible is false
        self._invincible = False
        self._switch_status = False



        # Wait for window to update before continuing
        master.update_idletasks()
        self.step()

        # create a pulldown menu, and add it to the menu bar
        menubar = tk.Menu(self._master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load Level", command=self.load_level)
        filemenu.add_command(label="Reset Level", command=self.reset_level)
        filemenu.add_command(label="High Scores", command=self.open_highscores)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._exit)

        menubar.add_cascade(label="File", menu=filemenu)
        self._master.config(menu=menubar)


        #make StatusDisplay appear on screen. healthprogress bar and score bar
        self._status_display = StatusDisplay(master,self._player,size)


    def load_level(self):
        """
        Prompts the user with a popup text input dialog.
        When the player inputs a level filename, load that level replacing the currently loaded level.
        """
        output = tk.simpledialog.askstring("Load Level", "Hi, please input the level name:")
        self._current_level=output
        self.reset_world(new_level=self._current_level)

    def reset_level(self):
        """
        Reset all player progress (e.g. health, score, etc) in the new current level.
        """
        self.reset_world(self._current_level)
        self._player._health=self._player.get_max_health()
        self._status_display.change()


    def _exit(self):
        """
        Prompts the user with a popup text ask him whether he wants to exit the game.

        """
        ans = messagebox.askokcancel('Verify exit', 'Really quit?')
        if ans:
            self._master.destroy()


    def reset_world(self, new_level):
        """
        Reset all player progress (e.g. health, score, etc) in the current level
        :param new_level(str): The game world file to load with blocks.

        """
        #block_sizea1 and block size2 is from config,means the position of player when he firstly appear in the game
        BLOCK_SIZE1=int(self._config.get_value('Player,x'))
        BLOCK_SIZE2 = int(self._config.get_value('Player,y'))
        mass=int(self._config.get_value('Player,mass'))
        self._world = load_world(self._builder, new_level)
        self._world.add_player(self._player, BLOCK_SIZE1, BLOCK_SIZE2,mass)

        self._builder.clear()

        self._setup_collision_handlers()

    def bind(self):
        """Bind all the keyboard events to their event handlers."""
        self._master.bind("<Left>", lambda e: self._move(-10, 0))
        self._master.bind("<Right>", lambda e: self._move(10, 0))
        self._master.bind("<Up>", lambda e: self._jump())
        self._master.bind("<Down>", lambda e: self._duck())
        self._master.bind("<space>", lambda e: self._jump())

        self._master.bind("a", lambda e: self._move(-10, 0))
        self._master.bind("d", lambda e: self._move(10, 0))
        self._master.bind("w", lambda e: self._jump())
        self._master.bind("s", lambda e: self._duck())


        self._master.bind("h", lambda e: self.open_highscores())
        self._master.bind("q", lambda e: self._exit())
        #bind 'keyboard events' and function lambda

        # in GUI, the top left point is (0,0), thus right is +1,left is -1(doesnt matter), up is -, down is +


    def open_highscores(self):
        """
        pop up a new custom window displaying the names and scores of the top ten highest scorers for the current level,
        sorted in descending order by score

        """
        filename= "scores "+self._current_level
        top = Toplevel()
        top.title("High Scores")
        for i in self._database.sort_list(filename):
            msg = Message(top, text=i)
            msg.pack()


    def redraw(self):
        """Redraw all the entities in the game canvas."""
        self._view.delete(tk.ALL)
        self._view.draw_entities(self._world.get_all_things())



    def scroll(self):
        """Scroll the view along with the player in the center unless
        they are near the left or right boundaries
        """
        x_position = self._player.get_position()[0]
        half_screen = self._master.winfo_width() / 2
        world_size = self._world.get_pixel_size()[0] - half_screen

        # Left side
        if x_position <= half_screen:
            self._view.set_offset((0, 0))

        # Between left and right sides
        elif half_screen <= x_position <= world_size:
            self._view.set_offset((half_screen - x_position, 0))

        # Right side
        elif x_position >= world_size:
            self._view.set_offset((half_screen - world_size, 0))

    def step(self):

        """Step the world physics and redraw the canvas."""

        if self._player.get_health()==0:
            #when health==0, popup a messagebox
            ans=messagebox.askokcancel("Dear, you are dead.","Do you want to restart or exit?")
            if ans:
                self._player._health = self._player.get_max_health()
                self._status_display.change()
                self.reset_world("level1.txt")
            else:
                self._master.destroy()
            #when player choose cancle, exit game

        data = (self._world, self._player)
        self._world.step(data)
        #justify whether time of invincible is over 10 seconds ,
        # when it is over, make player not invincible anymore.
        if self._player.is_invincible()==True:
            if time.time() - self._start > 10:
                self._player.set_invincible(False)
                self._status_display.change()

        # justify whether the time of switch is over 10 seconds, when it is over,
        # make disappeader bricks back
        if self._actived_switch is not None:
            if time.time()- self._actived_switch._switch_time1 >10:
                data = self._world, self._player
                self._actived_switch.recall_bricks(data)
                self._actived_switch._switch_status = False
                self._actived_switch = None



        self.scroll()
        self.redraw()

        self._master.after(10, self.step)


    def _move(self, dx, dy):
        """
        set player's velocity when he is moving
        :param dx:the increase velocity of x axis
        :param dy:the increase velocity of y axis

        """

        max_velocity = int(self._config.get_value('Player,max_velocity'))
        player_velocity = self._player.get_velocity()
        #use get_velocity method in class DynamicEntity(Entity) of entity.py

        if player_velocity.x + dx>=max_velocity:
            self._player.set_velocity((max_velocity, player_velocity.y))
        if player_velocity.x+dx<(-max_velocity):
            self._player.set_velocity((-max_velocity, player_velocity.y))
        else:
            self._player.set_velocity((player_velocity.x + dx, player_velocity.y))
        # player_velocity.x is used to get velocith of x of player,
        # player doesnt need acceleration when moving  in y direction, so doesnt need to +dy

    def _jump(self):
        """
        a function used when player jump
        """
        player_position = self._player.get_position()
        player_velocity = self._player.get_velocity()
        x_velocity = player_velocity[0]
        y_velocity = player_velocity[1]
        if self._world.get_block(player_position[0],player_position[1]+17) != None:
       # use get_velocity method in class DynamicEntity(Entity) of entity.py,player inherit it,so use player.
            self._player.set_velocity((x_velocity, -210))
        else:
            self._player.set_velocity((x_velocity, y_velocity))

        # in GUI, the positive direction of  y is down so here we set -130 is jumping



    def _duck(self):
        """
        a function used when player duck
:
        """
        player_velocity = self._player.get_velocity()
        # use get_velocity method in class DynamicEntity(Entity) of entity.py
        player_position=self._player.get_position()
        block=self._world.get_block(player_position[0],player_position[1]+17)
        # in GUI, the positive direction of  y is down so here we set +130 is ducking

        if block!= None:
            if block == "brick":
                self._player.set_velocity((player_velocity.x, 0))
                #mario cannot duck through the brick :)

            if self._world.get_block(player_position[0],player_position[1]+17).get_id() == "tunnel":
                if self._current_level == "level1.txt":
                    self._current_level =self._config.get_value('level1.txt,tunnel')
                    self.reset_world(self._current_level)
                if self._current_level == "level2.txt":
                    self._current_level =self._config.get_value('level2.txt,tunnel')
                    self.reset_world(self._current_level)





    def _setup_collision_handlers(self):
        self._world.add_collision_handler("player", "item", on_begin=self._handle_player_collide_item)
        self._world.add_collision_handler("player", "block", on_begin=self._handle_player_collide_block,
                                          on_separate=self._handle_player_separate_block)
        self._world.add_collision_handler("player", "mob", on_begin=self._handle_player_collide_mob)
        self._world.add_collision_handler("mob", "block", on_begin=self._handle_mob_collide_block)
        self._world.add_collision_handler("mob", "mob", on_begin=self._handle_mob_collide_mob)
        self._world.add_collision_handler("mob", "item", on_begin=self._handle_mob_collide_item)


    def _handle_mob_collide_block(self, mob: Mob, block: Block, data,
                                  arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the mob and a block.

        Parameters:
            mob (Mob): The mob that was involved in the collision
            block (Block): The block that the mob collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """
        direction=get_collision_direction(mob,block)
        if mob.get_id() == "fireball":
            if block.get_id() == "brick":
                self._world.remove_block(block)
            self._world.remove_mob(mob)

        if mob.get_id()== "mushroom":
        # when mushroom collides with a block, player, or other mob it should reverse its direction
            if direction=="L" or direction =="R":
                #"R" for Right, "L" for Left
                anti_vx= -mob.get_tempo()
                mob.set_tempo(anti_vx)

        if mob.get_id()== "koopa":
        # when koopa collides with a block, player, or other mob it should reverse its direction
            if direction=="L" or direction =="R":
                #"R" for Right, "L" for Left
                anti_vx= -mob.get_tempo()
                mob.set_tempo(anti_vx)

        return True



    def _handle_mob_collide_item(self, mob: Mob, block: Block, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        return False




    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:

        self._mob1 = mob1
        self._mob2 = mob2

        if mob1.get_id() == "fireball" or mob2.get_id() == "fireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

        if mob1.get_id()=="mushroom" or mob2.get_id()=="mushroom":
            # when mushroom collides with a mushroom it should reverse its direction
            vx_mob1 = mob1.get_tempo()
            vx_anti_mob1=-mob1.get_tempo()
            mob1.set_tempo(vx_anti_mob1)
            mob2.set_tempo(vx_mob1)

        return False




    def _handle_player_collide_item(self, player: Player, dropped_item: DroppedItem,
                                    data, arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the player and a (dropped) item. If the player has sufficient space in
        their to pick up the item, the item will be removed from the game world.

        Parameters:
            player (Player): The player that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the player collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """
        if dropped_item.get_id()=="coin":
            dropped_item.collect(self._player)
            self._world.remove_item(dropped_item)

        if dropped_item.get_id()=="star":
            dropped_item.collect(self._player)
            self._world.remove_item(dropped_item)
            # record the time player collect the star.(when player beclome invincible)
            self._start=time.time()
            self._player.set_invincible(True)

        self._status_display.change()
        return False



    def _handle_player_collide_block(self, player: Player, block: Block, data,
                                     arbiter: pymunk.Arbiter) -> bool:
        block.on_hit(arbiter, (self._world, player))
        direction = get_collision_direction(player, block)
        if block.get_id()=="goal":
        #popup simple dialog to record players' records
            if direction=="A":
                self._player._health = self._player.get_max_health()
                self._status_display.change()
            else:
                score = self._player.get_score()
                filename = "scores " + self._current_level
                name=tk.simpledialog.askstring("Please input your name", "Hi, please input your name:")
                if name!=None:
                    try:
                        with open(filename, 'a') as writer:
                            writer.write("name:" + name + ",scores:" + str(score))
                            writer.write('\n')

                    except FileNotFoundError:
                        print("File does not exist")
                    self._current_level = self._config.get_value(self._current_level + ',goal')
                    if self._current_level=='END':
                        ans = messagebox.askokcancel('Congratulations', 'Do you want to restart this game?')
                        if ans:
                            self._current_level="level1.txt"
                            player._health = self._player.get_max_health()
                            self._status_display.change()
                            self.reset_world(self._current_level)
                        else:
                            self._master.destroy()

                    else:
                        self.reset_world(self._current_level)
                if name==None:
                    self._current_level = self._config.get_value(self._current_level + ',goal')
                    if self._current_level == 'END':
                        ans = messagebox.askokcancel('Congratulations', 'Do you want to restart this game?')
                        if ans:
                            self._current_level = "level1.txt"
                            player._health = self._player.get_max_health()
                            self._status_display.change()
                            self.reset_world(self._current_level)

                        else:
                            self._master.destroy()
                    else:
                        self.reset_world(self._current_level)




        if block.get_id() == "switch":
            if block._switch_status == True:
                self._actived_switch = block
                return False
            # means the player will not collide with this switch block, switch can be passed through

        return True


    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:

        if self._player.is_invincible():
            self._world.remove_mob(mob)
        else:
            mob.on_hit(arbiter, (self._world, player))

        self._status_display.change()
        #bar become yellow
        return True


    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
        if block.get_id()=="bounce":
            block._anime = False
            #this is used for bounce animation
        return True


def main():
    #create a window
    root = tk.Tk()

    #give title to the window as"Mario"
    root.title('Mario')

    #invoke class MarioApp, and thus implement __init__method
    app = MarioApp(root)
    #cause the program to go into a loop waiting for any events
    root.mainloop()

if __name__ == "__main__":
    main()
