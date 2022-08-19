import pygame
import pygame.gfxdraw
import os
import sys
import json
from random import *
import time


def call_main():

    global main
    global window
    global game
    
    main = Main()
    window = Window()
    game = Game()
    new_interface = MainMenu()
    
    while main.running:
        main.loop()

class Main():

    def __init__(self):

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (40,100)
        pygame.init()
        pygame.font.init()

        self.__clock = pygame.time.Clock()
        self.__last_pressed_key_uni = ""
        self.__in_game = False
        self.__left_mouse_up = False
        self.__left_mouse_down = False
        self.__last_pressed_key = None
        self.__mouse_pos = (0,0)

        self.running = True
        self.random_territories = True
        self.cards_enabled = True
        self.colours = {"BLACK":(0,0,0),"WHITE":(255,255,255),"MAIN BLUE":(112,181,230),"OCEAN BLUE":(29,148,199),"GAME BACKGROUND":(66, 79, 102),
                        "SECONDARY BLUE":(47,94,128),"CLICKED BLUE":(39,80,110),"RED":(255,0,0),"GREEN":(0,255,0),"GREY":(186,189,194)}

    def loop(self):

        self.__mouse_pos = pygame.mouse.get_pos()

        self.__event_check()

        window.update()

        if self.__in_game:
            game.update()
            
        self.__clock.tick(60)
        
        pygame.display.flip()

    def unclick(self):

        self.__left_mouse_up = False

    def __event_check(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            if event.type == pygame.KEYDOWN:
                
                self.__last_pressed_key_uni = str(event.unicode)
                self.__last_pressed_key = event.key

                if event.key == pygame.K_ESCAPE:
                    self.running = False

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.__left_mouse_up = True
                
            else:
                self.__left_mouse_up = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.__left_mouse_down = True
            else:
                self.__left_mouse_down = False

    def get_attribute(self,attribute):

        if attribute == "mouse pos":
            return self.__mouse_pos
        elif attribute == "last pressed key":
            return self.__last_pressed_key
        elif attribute == "last pressed key uni":
            return self.__last_pressed_key_uni
        elif attribute == "in game":
            return self.__in_game
        elif attribute == "left mouse up":
            return self.__left_mouse_up
        elif attribute == "left mouse down":
            return self.__left_mouse_down

    def set_attribute(self,attribute,new):

        if attribute == "in game":
            self.__in_game = new
        elif attribute == "last pressed key":
            self.__last_pressed_key = new
        elif attribute == "last pressed key uni":
            self.__last_pressed_key_uni = new
        
        
class Window():

    def __init__(self):

        self.screen = pygame.display.set_mode((1200,700))
        
        self.__background = main.colours["SECONDARY BLUE"]
        self.__height,self.__width = pygame.display.Info().current_h, pygame.display.Info().current_w
        self.__grid_height,self.__grid_width = self.__height - 100,self.__width - 140

        self.__interfaces = []

    def update(self):
        
        self.screen.fill(self.__background)

        for territory in game.get_attribute("territories"):
            self.screen.blit(territory.get_attribute("surf"),territory.get_attribute("rect"))
            
        for territory in game.get_attribute("territories"):
            territory.draw_lines()

        for interface in self.__interfaces:
            interface.update()

        for dice in game.get_attribute("dice"):
            dice.update()

    def update_instruction_box(self,line,new_text):
        self.find_interface("game elements").change_element_text("instructionbox",new_text,line)

    def update_info_box(self,line,new_text):
        self.find_interface("game elements").change_element_text("infobox",new_text,line)

    def find_interface(self,interface_to_find):

        for interface in self.__interfaces:
            if interface.get_attribute("tag") == interface_to_find:
                return interface

    def delete_interface(self,interface_to_delete):
        
        for interface in self.__interfaces:
            if interface.get_attribute("tag") == interface_to_delete:
                interface.delete_self()

        if main.get_attribute("in game"):
            game.set_attribute("interface open",False)
          
    def get_attribute(self,attribute):

        if attribute == "background":
            return self.__background
        elif attribute == "height":
            return self.__height
        elif attribute == "width":
            return self.__width
        elif attribute == "grid height":
            return self.__grid_height
        elif attribute == "grid width":
            return self.__grid_width
        elif attribute == "interfaces":
            return self.__interfaces

    def set_attribute(self,attribute,new):

        if attribute == "background":
            self.__background = new
        if attribute == "interfraces":
            self.__interfaces = new

    def add_to_array(self,array,new):

        if array == "interfaces":
            self.__interfaces.append(new)

    def remove_from_array(self,array,removed):

        if array == "interfaces":
            self.__interfaces.remove(removed)
                      
class Game():

    def __init__(self):

        self.__num_of_players = 2
        self.__count = 0
        self.__troop_trade_in = 4
        self.__clicked_territory = ""
        self.__last_clicked_territory = ""
        self.__stored_territory = ""
        self.__stage = "draft"
        self.__interface_open = False
        self.__current_player = None
        self.__dice_x_position = 450
        self.__players = []
        self.__dice = []
        self.__red_dice = []
        self.__white_dice = []
        self.__territories = []
        self.__troop_counts = []

        self.__player_colours = [(0,98,255),(191,54,54),(0,255,242),(157,0,255),(26,255,0),(255,0,234),
                                 (255,106,0),(255,238,0),(10,105,18)]

        self.__continent_bonus_troops = {"North America":5,"South America":2,"Africa":3,"Europe":5,"Oceania":2,"Aisia":7}

        self.set_players(self.__num_of_players)

    def update(self):

        territory_info = self.__map.get_attribute("territory info")
                
        self.__update_territories()
            
        if self.__clicked_territory != "" and not self.__interface_open:

            if self.__stage == "occupy":
                
                self.__player_occupy(self.__clicked_territory)
                self.__check_if_territories_occupied()
                        
            elif self.__stage == "draft" and territory_info[self.__clicked_territory].occupant == self.__current_player:

                new_interface = Draft()
                
            elif self.__stage == "attack" and self.__last_clicked_territory != "" and self.__check_attack_conditions(territory_info):

                new_interface = Attack()
                self.__create_dice()

            elif self.__stage == "reinforce" and self.__last_clicked_territory != "" and self.__check_reinforce_conditions(territory_info):
                    
                if territory_info[self.__clicked_territory].occupant == self.__current_player and self.__clicked_territory != self.__last_clicked_territory:
                    
                    eligible_territories = self.__find_eligible_territories(self.__last_clicked_territory)

                    if self.__clicked_territory in eligible_territories:
                        new_interface = Reinforce()                   

            self.__last_clicked_territory = self.__clicked_territory
            
        self.__clicked_territory = ""

        if self.__current_player.get_attribute("draft troops") == 0 and self.__stage == "draft":
            self.__finish_draft()
       
    def start_game(self):

        window.set_attribute("background",main.colours["GAME BACKGROUND"])
        main.set_attribute("in game",True)
        self.__create_map()
        territory_info = self.__map.get_attribute("territory info")
        
        self.__count = randint(0,len(self.__players)-1)
        self.__current_player = self.__players[self.__count]
        for continent in self.__map.get_attribute("continents"):
            self.__current_player.check_if_continent_held(continent)
        
        if main.random_territories:
            new_interface = GameElements()
            self.__random_territories()
        else:
            self.__stage = "occupy"
            new_interface = GameElements()

        window.update_info_box(0,self.__current_player.ID + " holds " + str(len(self.__current_player.get_attribute("occupied territories"))) + " territories and " + 
                               str(len(self.__current_player.get_attribute("occupied continents"))) + " continents")
        window.update_info_box(1,"")
        window.update_info_box(2,"")
            
        self.__current_player.calculate_draft_troops()

    def check_players(self):

        for player in self.__players:
            if len(player.get_attribute("occupied territories")) == 0:
                self.__players.remove(player)
                window.find_interface("game elements").change_element_text("players","OUT",int(player.ID[7]))

        if len(self.__players) == 1:
            self.end_game()

    def set_players(self,amount):
        
        self.__num_of_players = amount
        self.__players = []
        for i in range(amount):
            self.__players.append(Player(i+1,self.__player_colours[i]))
            
    def switch_turn(self):

        self.__count += 1
        if self.__count > len(self.__players)-1:
            self.__count = 0
            
        if self.__current_player.get_attribute("territory won") and main.cards_enabled:
            self.__current_player.add_card()
            self.__current_player.set_attribute("territory won",False)
            
        self.__current_player = self.__players[self.__count]
        self.__current_player.calculate_draft_troops()

        for continent in self.get_continents():
            self.__current_player.check_if_continent_held(continent)

        for continent,troops in self.__continent_bonus_troops.items():
            if continent in self.__current_player.get_attribute("occupied continents"):
                self.__current_player.add_draft_troops(troops)

        if self.__stage != "occupy":
            self.__stage = "draft"
            window.find_interface("game elements").remove_element("endreinforce")
            window.update_instruction_box(0,game.get_attribute("current player").ID + ", click on one of your territories to draft in some troops.")
            window.update_instruction_box(1,"Draft all of your available troops to end the draft stage.")
            window.update_instruction_box(2,"")
        else:
            window.update_instruction_box(0,game.get_attribute("current player").ID + ", click on a territory to occupy it.")
            
        window.find_interface("game elements").change_element_text("players","Current Player: " + self.__current_player.ID)

    def end_game(self,*args):        
        main.set_attribute("in game",False)
        self.__territories = []
        window.find_interface("game elements").delete_self()
        window.set_attribute("background",main.colours["SECONDARY BLUE"])
        if len(args) == 1:
            new_interface = StartMenu()
        else:
            new_interface = Winner()
        self.__init__()
            
    def update_attack_text(self):
        
        attack_interface = window.find_interface("attack")
        territory_info = self.get_territory_info()
        attack_interface.change_element_text("mainsurf",self.__stored_territory + ":" + str(territory_info[self.__stored_territory].troops,),1)
        attack_interface.change_element_text("mainsurf",self.__last_clicked_territory + ":" + str(territory_info[self.__last_clicked_territory].troops),2)

    def end_attack(self):

        self.__stage = "reinforce"
        self.__last_clicked_territory = ""
        window.find_interface("game elements").remove_element("endattack")
        window.find_interface("game elements").inst_end_reinforce()
        window.update_instruction_box(0,"Click on one of YOUR territories containing at least 2 armies")
        window.update_instruction_box(1,"first, then click another one of YOUR other CONNECTED")
        window.update_instruction_box(2,"territories to reinforce it, or click the end reinforce stage button.")

    def end_reinforce(self):
        self.switch_turn()
        window.find_interface("game elements").remove_element("endreinforce")

    def remove_end_button(self):
        
        if self.__stage == "attack":
            window.find_interface("game elements").remove_element("endattack")
        elif self.__stage == "reinforce":
            window.find_interface("game elements").remove_element("endreinforce")
            

    def roll_dice(self):

        territory_info = self.__map.get_attribute("territory info")
        attacker = territory_info[self.__stored_territory].occupant
        
        for dice in self.__dice:
            dice.roll()

        dice_roll = True
        dice_roll_won = False
        while dice_roll:
            dice_roll,dice_roll_won,winner = self.__compare_dice()
            self.update_attack_text()
        self.__check_dice_amount()
        
        if dice_roll_won:
            if winner == attacker:
                self.__map.occupy_territory(attacker,self.__last_clicked_territory)
                self.__current_player.set_attribute("territory won",True)
                new_interface = Deploy()     
            self.reset_dice()
            window.delete_interface("attack")
                
        for dice in self.__dice:
            dice.set_attribute("used",False)

        window.find_interface("game elements").update_count(self.__stored_territory)
        window.find_interface("game elements").update_count(self.__last_clicked_territory)

    def add_dice(self):

        territory_info = self.__map.get_attribute("territory info")
        if len(self.__red_dice) < 3 and territory_info[game.get_attribute("stored territory")].troops - 1 != len(self.__red_dice):

            new_dice = Dice(main.colours["RED"],(self.__dice_x_position,640))
            self.__dice_x_position -= 50
                
            if len(self.__white_dice) == 1 and territory_info[game.get_attribute("last clicked territory")].troops != 1:
                new_dice = Dice(main.colours["WHITE"],(800,640))

    def remove_dice(self):

        if len(self.__red_dice) != 1:
            
            if len(self.__red_dice) == 2 and len(self.__white_dice) != 1:
                self.__white_dice[len(self.__white_dice)-1].delete()
            
            self.__red_dice[len(self.__red_dice)-1].delete()
            self.__dice_x_position += 50

    def reset_dice(self):

        for dice in self.__red_dice:
            self.__dice_x_position += 50
            del dice
                    
        self.__dice,self.__white_dice,self.__red_dice = [],[],[]

    def __compare_dice(self):

        territory_info = self.get_territory_info()
        
        highest_red_dice = None
        highest_white_dice = None

        attacking_troops = territory_info[self.__stored_territory].troops
        defending_troops = territory_info[self.__last_clicked_territory].troops

        if attacking_troops == 1:
            self.__dice_roll_won = True
            return False,True,territory_info[self.__last_clicked_territory].occupant
        elif defending_troops == 0:
            self.__dice_roll_won = True
            return False,True,territory_info[self.__stored_territory].occupant

        highest_red_dice = self.__get_highest_dice(self.__red_dice)
        highest_white_dice = self.__get_highest_dice(self.__white_dice)

        if highest_red_dice != None and highest_white_dice != None:
            
            if highest_red_dice.get_attribute("num") > highest_white_dice.get_attribute("num"):
                territory_info[self.__last_clicked_territory].troops -= 1
            else:
                territory_info[self.__stored_territory].troops -= 1

            highest_white_dice.set_attribute("used",True)
            highest_red_dice.set_attribute("used",True)
            
            return True,False,None

        else:
            return False,False,None

    def __get_highest_dice(self,dice_list):

        highest_dice = None
        for dice in dice_list:
            if not dice.get_attribute("used"):
                if highest_dice == None:
                    highest_dice = dice
                elif highest_dice.get_attribute("num") < dice.get_attribute("num"):
                    highest_dice = dice
        return highest_dice

    def __random_territories(self):
        
        self.__stage = "draft"
        done = False
        while not done:
            unoccupied = []
            for territory,info in self.get_territory_info().items():  
                if info.occupant == None and territory != "Ocean":
                    unoccupied.append(territory)
            if len(unoccupied) != 0:
                territory_to_occupy = unoccupied[randint(0,len(unoccupied)-1)]
                new_occupant = self.__find_weakest_player()
                self.__map.occupy_territory(new_occupant,territory_to_occupy)
                window.find_interface("game elements").update_count(territory_to_occupy)
            else:
                done = True

    def __find_weakest_player(self):

        weakest = None
        for player in self.__players:
            if weakest == None:
                weakest = player
            elif len(weakest.get_attribute("occupied territories")) > len(player.get_attribute("occupied territories")):
                weakest = player
        return weakest
        
    def __create_map(self):

        self.__map = Map()
        territory_info = self.__map.get_attribute("territory info")
        self.__fill_grid()
        self.__define_territories()

        for territory in self.__territories:            
            if territory.get_attribute("name") != "Ocean":
                territory.create_bounds()
                territory_info[territory.get_attribute("name")].territory_array.append(territory)
            
    def __fill_grid(self):

        full = False
        x_position, y_position = 140,100
        length = 20
        
        while not full:
            new_territory = Territory(x_position,y_position,length)
            self.__territories.append(new_territory)
            x_position += length

            if x_position == window.get_attribute("grid width"):
                x_position = 140
                y_position += length                
            if y_position == window.get_attribute("grid height"):
                full = True

    def __player_occupy(self,territory):
        
        territory_info = self.__map.get_attribute("territory info")
            
        if territory_info[territory].occupant == None:
            self.__map.occupy_territory(self.__current_player,territory)
            window.find_interface("game elements").update_count(territory)
            self.switch_turn()

    def __check_if_territories_occupied(self):

            territory_info = self.__map.get_attribute("territory info")
            
            count = 1
            for territory in territory_info:
                if territory_info[territory].occupant != None:
                    count += 1
                else:
                    break
            if count == len(territory_info):
                self.__stage = "draft"
                window.update_instruction_box(0,game.get_attribute("current player").ID + " click on a territory to draft in some troops.")
                window.update_instruction_box(1,"Draft all of your available troops to end the draft stage.")
                
                
    def __update_territories(self):
        for territory in self.__territories:
            territory.update()

        for positions in self.__map.get_attribute("connection positions"):
            pygame.draw.aaline(window.screen,main.colours["BLACK"],positions[0],positions[1])
        
    def __define_territories(self):

        n = 0
        for char in self.__map.get_attribute("text map"):
            
            if char != "00" and char !=  "\n":
                self.__territories[n].get_attribute("surf").fill(main.colours["GREY"])
                self.__territories[n].set_attribute("name",self.__map.get_attribute("territory names")[char])

            elif char == "00":
                self.__territories[n].get_attribute("surf").fill(main.colours["OCEAN BLUE"])
                self.__territories[n].set_attribute("name",self.__map.get_attribute("territory names")[char])

            if char != "\n" and char != "":
                n += 1

    def __check_attack_conditions(self,territory_info):
        if territory_info[self.__last_clicked_territory].troops != 1 and self.__last_clicked_territory in self.__map.get_attribute("adjacency dict")[self.__clicked_territory] and \
        self.__current_player == territory_info[self.__last_clicked_territory].occupant and self.__current_player != territory_info[self.__clicked_territory].occupant:
            return True

    def __check_reinforce_conditions(self,territory_info):
        if territory_info[self.__last_clicked_territory].occupant == self.__current_player and territory_info[self.__last_clicked_territory].troops != 1:
            return True

    def __finish_draft(self):
        self.__last_clicked_territory = ""
        self.__stage = "attack"
        window.find_interface("game elements").inst_end_attack()
        window.update_instruction_box(0,"Click on one of YOUR territories that has more than one army")
        window.update_instruction_box(1,"then click an adjacent ENEMY territory to attack it.")

    def __check_dice_amount(self):

        attacking_troops = self.__map.get_attribute("territory info")[self.__stored_territory].troops
        defending_troops = self.__map.get_attribute("territory info")[self.__last_clicked_territory].troops

        if attacking_troops == len(self.__red_dice):
            self.remove_dice()
        elif attacking_troops < len(self.__red_dice):
            self.remove_dice()
            self.remove_dice()
        if defending_troops < len(self.__white_dice):
            self.__white_dice[len(self.__white_dice)-1].delete()

    def __create_dice(self):

        new_dice = Dice(main.colours["RED"],(self.__dice_x_position,640))
        self.__dice_x_position -= 50
        new_dice = Dice(main.colours["WHITE"],(750,640))

    def __find_eligible_territories(self,current_territory):

        adjacency_dict = self.__map.get_attribute("adjacency dict")
        territory_info = self.__map.get_attribute("territory info")
        done = False
        visited = []
        queue = []
        
        while not done:
            visited.append(current_territory)
            for territory in adjacency_dict[current_territory]:
                if territory not in visited and territory not in queue and territory_info[territory].occupant == self.__current_player:
                    queue.append(territory)
            if len(queue) != 0:
                current_territory = queue[0]
                queue.remove(current_territory)
            else:
                done = True                
        return visited

    def get_attribute(self,attribute):
        
        if attribute == "num of players":
            return self.__num_of_players
        elif attribute == "players":
            return self.__players
        elif attribute == "interface open":
            return self.__interface_open
        elif attribute == "clicked territory":
            return self.__clicked_territory
        elif attribute == "last clicked territory":
            return self.__last_clicked_territory
        elif attribute == "stored territory":
            return self.__stored_territory
        elif attribute == "current player":
            return self.__current_player
        elif attribute == "territories":
            return self.__territories
        elif attribute == "dice":
            return self.__dice
        elif attribute == "stage":
            return self.__stage
        elif attribute == "troop trade in":
            return self.__troop_trade_in
        elif attribute == "player colours":
            return self.__player_colours
        
    def get_territory_info(self):
        return self.__map.get_attribute("territory info")

    def get_continents(self):
        return self.__map.get_attribute("continents")

    def get_trade_in_troops(self):

        troops_to_give = self.__troop_trade_in
        if self.__troop_trade_in == 12:
            self.__troop_trade_in += 3
        elif self.__troop_trade_in >= 15:
            self.__troop_trade_in += 5
        else:
            self.__troop_trade_in += 2
        return troops_to_give
        
    def set_attribute(self,attribute,new):

        if attribute == "num of players":
            self.__num_of_players = new
        elif attribute == "clicked territory":
            self.__clicked_territory = new
        elif attribute == "last clicked territory":
            self.__last_clicked_territory = new
        elif attribute == "stored territory":
            self.__stored_territory = new
        elif attribute == "stage":
            self.__stage = new
        elif attribute == "interface open":
            self.__interface_open = new

    def add_to_array(self,array,new):
        
        if array == "dice":
            self.__dice.append(new)
        elif array == "red dice":
            self.__red_dice.append(new)
        elif array == "white dice":
            self.__white_dice.append(new)
        elif array == "player colours":
            self.__player_colours.append(new)

    def remove_from_array(self,array,removed):

        if array == "red dice":
            self.__red_dice.remove(removed)
        elif array == "white dice":
            self.__white_dice.remove(removed)
        elif array == "dice":
            self.__dice.remove(removed)
        elif array == "player colours":
            self.__player_colours.remove(removed)

            

class Player():

    def __init__(self,num,colour):

        self.__colour = colour
        self.__draft_troops = 0
        self.__num = num
        self.__territory_won = False

        self.__occupied_territories = []
        self.__occupied_continents = []
        self.__cards = []
        self.__troops_to_distribute = [5,4,4,3,3,3]

        self.ID = str("Player " + str(num))

    def check_if_continent_held(self,continent):

        continents = game.get_continents()
        territory_array = continents[continent]

        for territory in territory_array:
            if territory not in self.__occupied_territories:
                if continent in self.__occupied_continents:
                    self.__occupied_continents.remove(continent)
                return
            
        if continent not in self.__occupied_continents:
            self.__occupied_continents.append(continent)
            window.update_info_box(2, self.ID + " occupied the continent: " + continent)
                
    def calculate_draft_troops(self):
        
        self.__draft_troops = len(self.__occupied_territories)//3

        if self.__draft_troops < 3:
            self.__draft_troops = 3

    def switch_colour(self):

        for colour in game.get_attribute("player colours"):
            colour_taken = False
            for player in game.get_attribute("players"):
                if player.get_attribute("colour") == colour:
                    colour_taken = True
            if not colour_taken:
                game.remove_from_array("player colours",self.__colour)
                game.add_to_array("player colours",self.__colour)
                self.__colour = colour
                return
            
    def trade_cards_in(self):

        empty = 0
        type_dict = {"infantry":[],"cavalry":[],"artillery":[],"wild":[]}
        
        for card in self.__cards:
            type_dict[card.get_attribute("type")].append(card)
            
        for type_,array in type_dict.items():
            if len(array) >= 3:
                window.update_info_box(2,self.ID + " traded in cards for " + str(game.get_attribute("troop trade in")) + " troops")
                self.__draft_troops += game.get_trade_in_troops()
                for i in range(3):
                    self.__cards.remove(array[i])
                    window.find_interface("cards").remove_element(array[i])
                    game.remove_end_button()
                    game.set_attribute("stage","draft")
                return
            elif len(array) == 0:
                empty += 1
                    
        if empty <= 1:
            window.update_info_box(2,self.ID + " traded in cards for " + str(game.get_attribute("troop trade in")) + " troops")
            self.__draft_troops += game.get_trade_in_troops()
            count = 0
            for type_,array in type_dict.items():
                if len(array) != 0 and count != 3:
                    self.__cards.remove(array[0])
                    window.find_interface("cards").remove_element(array[0])
                    game.remove_end_button()
                    game.set_attribute("stage","draft")
                    count += 1
            return

        if len(window.find_interface("cards").find_element("mainsurf").get_attribute("text objects")) == 1:
            window.find_interface("cards").find_element("mainsurf").write("Cannot trade in",(495,40),"biome",main.colours["RED"],22)

    def distribute_troop(self):

        if len(self.__troops_to_distribute) != 0:
            index = randint(0,len(self.__troops_to_distribute)-1)
            amount = self.__troops_to_distribute[index]
            self.__troops_to_distribute.pop(index)
        else:
            amount = randint(1,2)
        return amount
        
    def add_card(self):

        if len(self.__cards) < 6:
            types = ["infantry","cavalry","artillery"]
            i = randint(1,22)
            if i == 22:
                self.__cards.append(Card("wild"))
            else:
                self.__cards.append(Card(types[randint(0,2)]))
                                

    def add_draft_troops(self,new_troops):
        self.__draft_troops += new_troops
        
    def get_attribute(self,attribute):

        if attribute == "colour":
            return self.__colour
        elif attribute == "draft troops":
            return self.__draft_troops
        elif attribute == "occupied continents":
            return self.__occupied_continents
        elif attribute == "occupied territories":
            return self.__occupied_territories
        elif attribute == "territory won":
            return self.__territory_won
        elif attribute == "cards":
            return self.__cards

    def set_attribute(self,attribute,new):

        if attribute == "draft troops":
            self.__draft_troops = new
        if attribute == "colour":
            self.__colour = new
        if attribute == "territory won":
            self.__territory_won = new

    def add_to_array(self,array,new):
        
        if array == "occupied territories":
            self.__occupied_territories.append(new)

    def remove_from_array(self,array,removed):

        if array == "occupied territories":
            self.__occupied_territories.remove(removed)
            
class Interface():

    def __init__(self,tag):
        self._tag = tag
        self._elements = []
        window.add_to_array("interfaces",self)

    def update(self):
        
        for element in self._elements:
            element.update()

    def find_element(self,element_to_find):

        element_to_return = None

        for element in self._elements:
            if element.get_attribute("tag") == element_to_find:
                element_to_return = element

        return element_to_return

    def change_element_text(self,*args):

        element = args[0]
        new_text = args[1]
        
        for e in self._elements:
            if e.get_attribute("tag") == element:
                if len(args) == 2:
                    e.update_text(0,new_text)
                else:
                    e.update_text(args[2],new_text)
                
    def delete_self(self):

        self._elements = []
        window.remove_from_array("interfaces",self)

    def __create_elements(self):
        pass
    

    def get_attribute(self,attribute):

        if attribute == "tag":
            return self._tag
        elif attribute == "elements":
            return self._elements

    def add_element(self,new):
        
        self._elements.append(new)

    def remove_element(self,remove_tag):
        
        if isinstance(remove_tag,str):
            for element in self._elements:
                if element.get_attribute("tag") == remove_tag:
                    self._elements.remove(element)
        else:
            for element in self._elements:
                if element == remove_tag:
                    self._elements.remove(element)

class MainMenu(Interface):

    def __init__(self):

        super().__init__("main menu")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 4
        for i in range(num_of_elements):
            if i == 0:
                new_element = Plane((800,650),(200,25),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("RISK",(270,150),"biome",main.colours["SECONDARY BLUE"],150)

            elif i == 1:
                new_element = Button((400,50),(400,450),main.colours["SECONDARY BLUE"],"start",self)
                new_element.write("START",(145,9),"biome",main.colours["MAIN BLUE"],50)

            elif i == 2:
                new_element = Button((400,50),(400,525),main.colours["SECONDARY BLUE"],"settings",self)           
                new_element.write("SETTINGS",(110,9),"biome",main.colours["MAIN BLUE"],50)

            elif i == 3:
                new_element = Button((70,30),(225,45),main.colours["SECONDARY BLUE"],"exit",self)
                new_element.write("EXIT",(10,6),"biome",main.colours["MAIN BLUE"],30)
                
            self._elements.append(new_element)

class StartMenu(Interface):

    def __init__(self):
        
        super().__init__("start menu")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 5
        for i in range(num_of_elements):
            if i == 0:
                new_element = Plane((800,650),(200,25),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("RISK",(270,150),"biome",main.colours["SECONDARY BLUE"],150)
                new_element.write("NUMBER OF PLAYERS:",(100,400),"biome",main.colours["SECONDARY BLUE"],30)
                new_element.write("COLOUR CHOICE:",(450,400),"biome",main.colours["SECONDARY BLUE"],30)

            elif i == 1:
                new_element = Button((70,30),(225,45),main.colours["SECONDARY BLUE"],"back",self)
                new_element.write("BACK",(7,6),"biome",main.colours["MAIN BLUE"],30)

            elif i == 2:
                new_element = Button((225,20),(300,450),main.colours["SECONDARY BLUE"],"players",self)
                new_element.write(str(game.get_attribute("num of players")),(110,2),"biome",main.colours["MAIN BLUE"],25)

            elif i == 3:
                new_element = Button((225,20),(650,450),main.colours["SECONDARY BLUE"],"colours",self)
                new_element.write("CHOOSE COLOURS",(55,3),"biome",main.colours["MAIN BLUE"],20)

            elif i == 4:
                new_element = Button((400,50),(400,550),main.colours["SECONDARY BLUE"],"play",self)
                new_element.write("PLAY",(140,9),"biome",main.colours["MAIN BLUE"],50)
                
            self._elements.append(new_element)

class PlayerChoice(Interface):

    def __init__(self):

        super().__init__("player choice")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 3
        positions = [(490,300),(350,350),(350,400),(625,350),(625,400)]
        
        for i in range(num_of_elements):    
            if i == 0:
                new_element = Plane((600,300),(300,200),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("CHOOSE NUMBER OF PLAYERS",(150,15),"biome",main.colours["SECONDARY BLUE"],30)

            elif i == 1:
                new_element = Button((70,30),(310,210),main.colours["SECONDARY BLUE"],"back",self)
                new_element.write("BACK",(7,6),"biome",main.colours["MAIN BLUE"],30)

            elif i == 2:
                for n in range(5):
                    new_element = Button((225,20),positions[n],main.colours["SECONDARY BLUE"],str(n+2),self)
                    new_element.write(str(n+2),(110,2),"biome",main.colours["MAIN BLUE"],25)
                    self._elements.append(new_element)

            if new_element not in self._elements:
                self._elements.append(new_element)

class ColourChoice(Interface):

    def __init__(self):

        super().__init__("colour choice")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 3
        
        for i in range(num_of_elements):    
            if i == 0:
                height = 90
                new_element = Plane((600,300),(300,200),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("CHOOSE PLAYER COLOURS",(150,15),"biome",main.colours["SECONDARY BLUE"],30)
                new_element.write("click the squares to change the colour",(10,50),"biome",main.colours["SECONDARY BLUE"],20)
                
                for n in range(0,game.get_attribute("num of players")):
                    new_element.write("Player " + str(n+1) + ":",(40,height),"biome",main.colours["WHITE"],30)
                    height += 30

            elif i == 1:
                new_element = Button((70,30),(310,210),main.colours["SECONDARY BLUE"],"back",self)
                new_element.write("BACK",(7,6),"biome",main.colours["MAIN BLUE"],30)

            elif i == 2:
                height = 290
                for n in range(0,game.get_attribute("num of players")):
                    new_element = Button((50,20),(440,height),game.get_attribute("players")[n].get_attribute("colour"),"colourblock" + str(n+1),self)
                    height += 30
                    self._elements.append(new_element)

            if new_element not in self._elements:
                self._elements.append(new_element)

class Settings(Interface):

    def __init__(self):

        super().__init__("settings")
        self.__create_elements()

    def __create_elements(self):

        num_of_elements = 4
        for i in range(num_of_elements):
            if i == 0:
                new_element = Plane((600,300),(300,200),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("SETTINGS",(220,50),"biome",main.colours["SECONDARY BLUE"],40)
                new_element.write("RANDOM TERRITORIES?",(50,150),"biome",main.colours["SECONDARY BLUE"],20)
                new_element.write("ALLOW CARDS?",(375,150),"biome",main.colours["SECONDARY BLUE"],20)

            elif i == 1:
                new_element = Button((70,30),(310,210),main.colours["SECONDARY BLUE"],"back",self)
                new_element.write("BACK",(7,6),"biome",main.colours["MAIN BLUE"],30)

            elif i == 2:
                new_element = Button((50,20),(400,375),main.colours["SECONDARY BLUE"],"toggle 1",self)
                if main.random_territories:
                    new_element.write("YES",(8,2),"biome",main.colours["MAIN BLUE"],25)
                else:
                    new_element.write("NO",(8,2),"biome",main.colours["MAIN BLUE"],25)
                    
            elif i == 3:
                new_element = Button((50,20),(700,375),main.colours["SECONDARY BLUE"],"toggle 2",self)
                if main.cards_enabled:
                    new_element.write("YES",(8,2),"biome",main.colours["MAIN BLUE"],25)
                else:
                    new_element.write("NO",(8,2),"biome",main.colours["MAIN BLUE"],25)
                
            self._elements.append(new_element)
    
class Draft(Interface):

    def __init__(self):

        super().__init__("draft")
        self.__create_elements()
        
    def __create_elements(self):
        
        num_of_elements = 3
        game.set_attribute("interface open",True)
        window.update_instruction_box(0,"Type the number of armies you would like to transfer.")
        window.update_instruction_box(1,"")
        
        for i in range(num_of_elements):
            if i == 0:
                new_element = Plane((250,75),(475,610),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("DRAFT",(96,2),"biome",main.colours["WHITE"],25)
                new_element.write("Troops Available:",(10,23),"biome",main.colours["WHITE"],15)
                new_element.write(str(game.get_attribute("current player").get_attribute("draft troops")),(100,23),"biome",main.colours["WHITE"],15)

            elif i == 1:
                new_element = TextBox((50,20),(575,650),main.colours["SECONDARY BLUE"],"troops",self)
                new_element.write(str(new_element.get_attribute("entry text")),(13,2),"biome",main.colours["WHITE"],22)

            elif i == 2:
                new_element = Button((20,20),(703,612),main.colours["SECONDARY BLUE"],"exitinter",self)
                new_element.write("X",(3,0),"biome",main.colours["WHITE"],31)
                
            self._elements.append(new_element)

class Attack(Interface):

    def __init__(self):
        
        super().__init__("attack")
        self.__create_elements()

    def __create_elements(self):
    
        num_of_elements = 5
        last_clicked_territory = game.get_attribute("last clicked territory")
        clicked_territory = game.get_attribute("clicked territory")
        game.set_attribute("interface open",True)
        window.update_instruction_box(0,"Click the plus to add dice, click roll to roll the dice.")
        window.update_instruction_box(1,"Troops from each territory will be taken away accordingly.")
        
        
        for i in range(num_of_elements):
            if i == 0:
                new_element = Plane((920,75),(140,610),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("ATTACK",(444,2),"biome",main.colours["WHITE"],25)
                new_element.write(game.get_attribute("last clicked territory") + ": " + str(game.get_territory_info()[last_clicked_territory].troops),(230,10),"biome",main.colours["WHITE"],20)
                game.set_attribute("stored territory",last_clicked_territory)
                new_element.write(clicked_territory + ": " + str(game.get_territory_info()[clicked_territory].troops),(690,10),"biome",main.colours["WHITE"],20)
                new_element.write("NUMBER OF DICE",(15,15),"biome",main.colours["WHITE"],20)
                
            elif i == 1:
                new_element = Button((50,20),(590,650),main.colours["SECONDARY BLUE"],"roll",self)
                new_element.write("ROLL",(5,3),"biome",main.colours["WHITE"],22)

            elif i == 2:
                new_element = Button((20,20),(1038,612),main.colours["SECONDARY BLUE"],"exitinter",self)
                new_element.write("X",(3,0),"biome",main.colours["WHITE"],31)

            elif i == 3:
                new_element = Button((20,20),(230,650),main.colours["SECONDARY BLUE"],"plus",self)
                new_element.write("+",(4,0),"biome",main.colours["WHITE"],31)

            elif i == 4:
                new_element = Button((20,20),(170,650),main.colours["SECONDARY BLUE"],"minus",self)
                new_element.write("-",(6,0),"biome",main.colours["WHITE"],31)
                                
            self._elements.append(new_element)

class Deploy(Interface):

    def __init__(self):

        super().__init__("deploy")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 2
        game.set_attribute("interface open",True)
        window.update_instruction_box(0,"Type the number of armies you would like to transfer.")
        window.update_instruction_box(1,"")
        
        for i in range(num_of_elements):
            if i == 0:
                new_element = Plane((250,75),(475,610),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("DEPLOY",(96,2),"biome",main.colours["WHITE"],25)
                new_element.write("Troops Available:",(10,23),"biome",main.colours["WHITE"],15)
                new_element.write(str(game.get_territory_info()[game.get_attribute("stored territory")].troops - 1),(100,23),"biome",main.colours["WHITE"],15)

            elif i == 1:
                new_element = TextBox((50,20),(575,650),main.colours["SECONDARY BLUE"],"deploy",self)
                new_element.write(str(new_element.get_attribute("entry text")),(13,2),"biome",main.colours["WHITE"],22)                
                
            self._elements.append(new_element)

class Reinforce(Interface):

    def __init__(self):

        super().__init__("reinforce")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 3
        last_clicked_territory = game.get_attribute("last clicked territory")
        game.set_attribute("interface open",True)
        window.update_instruction_box(0,"Type the number of armies you would like to transfer.")
        window.update_instruction_box(1,"")
        window.update_instruction_box(2,"")
        
        for i in range(num_of_elements):
            if i == 0:
                new_element = Plane((250,75),(475,610),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("REINFORCE",(96,2),"biome",main.colours["WHITE"],25)
                new_element.write("Troops Available:",(10,23),"biome",main.colours["WHITE"],15)
                new_element.write(str(game.get_territory_info()[last_clicked_territory].troops - 1),(100,23),"biome",main.colours["WHITE"],15)
                game.set_attribute("stored territory",last_clicked_territory)

            elif i == 1:
                new_element = TextBox((50,20),(575,650),main.colours["SECONDARY BLUE"],"reinforce",self)
                new_element.write(str(new_element.get_attribute("entry text")),(13,2),"biome",main.colours["WHITE"],22)

            elif i == 2:
                new_element = Button((20,20),(703,612),main.colours["SECONDARY BLUE"],"exitinter",self)
                new_element.write("X",(3,0),"biome",main.colours["WHITE"],31)
                
            self._elements.append(new_element)

class GameElements(Interface):

    def __init__(self):

        super().__init__("game elements")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 7
        territory_info = game.get_territory_info()
        count_positions = json.load(open("JSON files/count positions.JSON"))

        for i in range(num_of_elements):

            if i == 0:
                height = 30
                new_element = Plane((130,130),(1065,50),main.colours["MAIN BLUE"],"players",self)
                new_element.write("Current Player: " + game.get_attribute("current player").ID,(5,10),"biome",main.colours["WHITE"],15)
                for n in range(0,game.get_attribute("num of players")):
                    new_element.write("Player " + str(n+1) + ":",(10,height),"biome",main.colours["WHITE"],20)
                    height += 15
                    
            elif i == 1:
                height = 82
                for n in range(0,game.get_attribute("num of players")):
                    new_element = Plane((10,10),(1150,height),game.get_attribute("players")[n].get_attribute("colour"),"colourblock",self)
                    height += 15
                    self._elements.append(new_element)

            elif i == 2:
                for territory in territory_info:
                    if territory != "Ocean":
                        if territory in count_positions:
                            new_element = Plane((20,15),tuple(count_positions[territory]),main.colours["RED"],territory,self)
                        else:
                            new_element = Plane((20,15),
                                                territory_info[territory].territory_array[int(len(territory_info[territory].territory_array)/2)].get_attribute("rect").topleft,
                                                main.colours["RED"],territory,self)
                        new_element.write(str(territory_info[territory].troops),(2,3),"biome",main.colours["WHITE"],15)
                        game.get_territory_info()[territory].troop_count = new_element
                        self._elements.append(new_element)

            elif i == 3:
                if main.cards_enabled:
                    new_element = Button((130,15),(1065,185),main.colours["MAIN BLUE"],"cardshow",self)
                    new_element.write("Show cards",(35,2),"biome",main.colours["WHITE"],17)

            elif i == 4:
                new_element = Plane((400,60),(10,10),main.colours["MAIN BLUE"],"instructionbox",self)
                
                if game.get_attribute("stage") == "occupy":
                    new_element.write(game.get_attribute("current player").ID + ", click on a territory to occupy it.",(3,3),"biome",main.colours["WHITE"],20)
                    new_element.write("",(3,18),"biome",main.colours["WHITE"],20)
                else:
                    new_element.write(game.get_attribute("current player").ID + ", click on one of your territories to draft in some troops.",(3,3),"biome",main.colours["WHITE"],20)
                    new_element.write("Draft all of your available troops to end the draft stage.",(3,18),"biome",main.colours["WHITE"],20)
                new_element.write("",(3,33),"biome",main.colours["WHITE"],20)

            elif i == 5:
                new_element = Plane((310,60),(420,10),main.colours["MAIN BLUE"],"infobox",self)              
                new_element.write("",(3,3),"biome",main.colours["WHITE"],20)
                new_element.write("",(3,18),"biome",main.colours["WHITE"],20)
                new_element.write("",(3,33),"biome",main.colours["WHITE"],20)

            elif i == 6:
                new_element = Button((100,15),(10,75),main.colours["MAIN BLUE"],"exitgame",self)
                new_element.write("EXIT GAME",(20,3),"biome",main.colours["WHITE"],17)
    
            if new_element not in self._elements:
                self._elements.append(new_element)

    def update_count(self,territory):

        self.change_element_text(territory,str(game.get_territory_info()[territory].troops))

    def inst_end_attack(self):

        new_element = Button((130,15),(1065,205),main.colours["MAIN BLUE"],"endattack",self)
        new_element.write("End attack stage",(20,2),"biome",main.colours["WHITE"],17)
        self._elements.append(new_element)

    def inst_end_reinforce(self):

        new_element = Button((130,15),(1065,205),main.colours["MAIN BLUE"],"endreinforce",self)
        new_element.write("End reinforce stage",(18,2),"biome",main.colours["WHITE"],17)
        self._elements.append(new_element)

class Winner(Interface):

    def __init__(self):

        super().__init__("winner")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 2

        for i in range(num_of_elements):

            if i == 0:
                new_element = Plane((600,300),(300,200),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write(game.get_attribute("current player").ID + " Wins!",(200,100),"biome",main.colours["SECONDARY BLUE"],40)
                    
            elif i == 1:
                new_element = Button((400,50),(400,400),main.colours["SECONDARY BLUE"],"back",self)
                new_element.write("BACK TO MENU",(65,9),"biome",main.colours["MAIN BLUE"],50)

            self._elements.append(new_element)

class Cards(Interface):

    def __init__(self):

        super().__init__("cards")
        self.__create_elements()

    def __create_elements(self):
        
        num_of_elements = 4
        current_player = game.get_attribute("current player")
        game.set_attribute("interface open",True)

        for i in range(num_of_elements):

            if i == 0:
                new_element = Plane((610,85),(295,605),main.colours["MAIN BLUE"],"mainsurf",self)
                new_element.write("CARDS",(520,10),"biome",main.colours["WHITE"],22)

            elif i == 1:
                xval = 305
                for card in current_player.get_attribute("cards"):
                    card.set_attribute("pos",(xval,610))
                    new_element = card
                    self._elements.append(new_element)
                    xval += 60
                        
            elif i == 2:
                new_element = Button((20,20),(882,608),main.colours["SECONDARY BLUE"],"exitinter",self)
                new_element.write("X",(3,0),"biome",main.colours["WHITE"],31)

            elif i == 3:
                new_element = Button((100,20),(800,665),main.colours["SECONDARY BLUE"],"tradein",self)
                new_element.write("TRADE IN",(14,4),"biome",main.colours["WHITE"],22)

            if new_element not in self._elements:
                self._elements.append(new_element)

    
class InterfaceElement():

    def __init__(self,dimensions,pos,colour,tag,type_,interface):
        
        self._colour, self._original_colour = colour, colour
        self._surf = pygame.Surface(dimensions)
        self._rect = self._surf.get_rect(topleft=pos)
        self._tag = tag
        self._type = type_
        self._interface = interface

        self._text_objects = []
        self._rect_corners = [(self._rect.topleft,self._rect.topright),(self._rect.topright,self._rect.bottomright),
                             (self._rect.bottomright,self._rect.bottomleft),(self._rect.bottomleft,self._rect.topleft)]

    def update(self):

        screen = window.screen
        self._check_interaction()                
        self._surf.fill(self._colour)                        
        for text in self._text_objects:
            self._surf.blit(text.get_attribute("surf"),text.get_attribute("pos"))
            
        screen.blit(self._surf,self._rect)
        self.__draw_outlines(screen)

    def _check_interaction(self):
        pass

    def update_text(self,index,new_text):

        try:
            text_to_change = self._text_objects[index]
            text_to_change.set_attribute("surf",text_to_change.get_attribute("font").render(new_text,True,text_to_change.get_attribute("colour")))
        except IndexError:
            pass
        
    def write(self,text,pos,font,colour,size):
        new_text = Text(text,pos,font,colour,size)
        self._text_objects.append(new_text)

    def delete(self):

        self._interface.delete_self()

    def __draw_outlines(self,screen):
        for corner_coord in self._rect_corners:
            pygame.draw.line(screen,main.colours["BLACK"],corner_coord[0],corner_coord[1])

    def get_attribute(self,attribute):

        if attribute == "entry text":
            return self._entry_text
        if attribute == "text objects":
            return self._text_objects
        if attribute == "tag":
            return self._tag


class Plane(InterfaceElement):

    def __init__(self,dimensions,pos,colour,tag,interface):

        super().__init__(dimensions,pos,colour,tag,"plane",interface)

class Button(InterfaceElement):

    def __init__(self,dimensions,pos,colour,tag,interface):

        super().__init__(dimensions,pos,colour,tag,"button",interface)

    def _check_interaction(self):

        mouse_pos = main.get_attribute("mouse pos")
        
        if self._rect.collidepoint(mouse_pos) and main.get_attribute("left mouse down") and not game.get_attribute("interface open") and self._tag[0:11] != "colourblock":          
            self._colour = main.colours["CLICKED BLUE"]
        
        if main.get_attribute("left mouse up"):

            if self._tag[0:11] != "colourblock":
                self._colour = self._original_colour
            
            if self._rect.collidepoint(mouse_pos):
            
                if self._tag == "exit":                
                    main.running = False

                elif self._tag == "start":                
                    self.delete()
                    new_interface = StartMenu()

                elif self._tag == "settings":                
                    self.delete()
                    new_interface = Settings()
                    
                elif self._tag == "back":                
                    self.delete()
                    if self._interface.get_attribute("tag") == "player choice" or self._interface.get_attribute("tag") == "colour choice":                    
                        new_interface = StartMenu()
                    else:               
                        new_interface = MainMenu()
                        game.set_attribute("num of players",2)

                elif self._tag == "players":            
                    self.delete()
                    new_interface = PlayerChoice()

                elif self._tag == "colours":
                    self.delete()
                    new_interface = ColourChoice()

                elif self._tag == "play":                
                    self.delete()
                    game.start_game()

                elif self._tag == "exitinter":
                    self.delete()
                    if game.get_attribute("stage") == "attack":
                        game.reset_dice()
                        window.update_instruction_box(0,game.get_attribute("current player").ID + ", click on one of YOUR territories that has more than")
                        window.update_instruction_box(1,"one army, then click an adjacent ENEMY territory to attack it.")
                    elif game.get_attribute("stage") == "reinforce":
                        game.set_attribute("last clicked territory","")
                        window.update_instruction_box(0,"Click on one of YOUR territories containing at least 2 armies")
                        window.update_instruction_box(1,"first, then click another one of YOUR other CONNECTED")
                        window.update_instruction_box(2,"territories to reinforce it.")
                    elif game.get_attribute("stage") == "draft":
                        window.update_instruction_box(0,game.get_attribute("current player").ID + ", click on one of your territories to draft in some troops.")
                        window.update_instruction_box(1,"Draft all of your available troops to end the draft stage.")
                    game.set_attribute("interface open",False)

                elif self._tag == "plus":
                    game.add_dice()

                elif self._tag == "minus":
                    game.remove_dice()

                elif self._tag == "tradein":
                    game.get_attribute("current player").trade_cards_in()
                    
                elif self._tag == "roll":                        
                    game.roll_dice()

                elif self._tag.isdigit():
                    game.set_players(int(self._tag))
                    self.delete()
                    new_interface = StartMenu()

                elif self._tag[0:6] == "toggle":
                    if self._tag[7] == "1":
                        main.random_territories = not main.random_territories
                        if main.random_territories:
                            self.update_text(0,"YES")
                        else:
                            self.update_text(0,"NO")
                    if self._tag[7] == "2":
                        main.cards_enabled = not main.cards_enabled
                        if main.cards_enabled:
                            self.update_text(0,"YES")
                        else:
                            self.update_text(0,"NO")
                            
                elif self._interface.get_attribute("tag") == "colour choice" and self._tag[0:11] == "colourblock":
                    game.get_attribute("players")[int(self._tag[11])-1].switch_colour()
                    self._colour = game.get_attribute("players")[int(self._tag[11])-1].get_attribute("colour")

                if not game.get_attribute("interface open"):                
                    if self._tag == "endattack":
                        game.end_attack()
                    elif self._tag == "endreinforce":
                        game.end_reinforce()
                    elif self._tag == "cardshow":
                        window.update_instruction_box(0,"Click trade in if you have an eligible set of cards.")
                        window.update_instruction_box(1,"")
                        window.update_instruction_box(2,"")
                        new_interface = Cards()
                    elif self._tag == "exitgame":
                        game.end_game("not won")
                    
                main.unclick()

class TextBox(InterfaceElement):

    def __init__(self,dimensions,pos,colour,tag,interface):

        super().__init__(dimensions,pos,colour,tag,"text box",interface)
        self._entry_text = ""
        
    def _check_interaction(self):
        
        territory_info = game.get_territory_info()
        last_clicked_territory = game.get_attribute("last clicked territory")
        stored_territory = game.get_attribute("stored territory")
        last_pressed_key = main.get_attribute("last pressed key")

        if last_pressed_key == pygame.K_BACKSPACE:
            self._entry_text = self._entry_text[:-1]
            main.set_attribute("last pressed key", None)

        elif last_pressed_key == pygame.K_RETURN and self._entry_text != "0" and self._entry_text != "":
                
            if self._interface.get_attribute("tag") == "draft":
                self.__draft(territory_info,last_clicked_territory,stored_territory)

            elif self._interface.get_attribute("tag") == "deploy":
                self.__deploy(territory_info,last_clicked_territory,stored_territory)

            elif self._interface.get_attribute("tag") == "reinforce":
                self.__reinforce(territory_info,last_clicked_territory,stored_territory)

            main.set_attribute("last pressed key",None)
            game.set_attribute("interface open", False)

        else:
            if main.get_attribute("last pressed key uni").isdigit() and len(self._entry_text) < 3:                
                self._entry_text += main.get_attribute("last pressed key uni")
        self._text_objects[0].set_attribute("surf",self._text_objects[0].get_attribute("font").render(self._entry_text,True,self._text_objects[0].get_attribute("colour"))) 
        main.set_attribute("last pressed key uni","")

    def __draft(self,territory_info,last_clicked_territory,stored_territory):
        
        draft_troops = game.get_attribute("current player").get_attribute("draft troops")
        if draft_troops >= int(self._entry_text):
            game.get_attribute("current player").set_attribute("draft troops",(draft_troops - int(self._entry_text))) 
            territory_info[last_clicked_territory].troops += int(self._entry_text)
            window.find_interface("game elements").update_count(last_clicked_territory)
            self.delete()

        if game.get_attribute("current player").get_attribute("draft troops") != 0:
            window.update_instruction_box(0,game.get_attribute("current player").ID + ", click on one of your territories to draft in some troops.")
            window.update_instruction_box(1,"Draft all of your available troops to end the draft stage.")

    def __deploy(self,territory_info,last_clicked_territory,stored_territory):
        
        deploy_troops = territory_info[game.get_attribute("stored territory")].troops - 1
        if deploy_troops >= int(self._entry_text):
            self.__transfer(territory_info,last_clicked_territory,stored_territory)
            window.update_instruction_box(0,game.get_attribute("current player").ID + ", click on one of YOUR territories that has more than")
            window.update_instruction_box(1,"one army, then click an adjacent ENEMY territory to attack it.")
            game.set_attribute("last clicked territory","")
            self.delete()
            game.check_players()

    def __reinforce(self,territory_info,last_clicked_territory,stored_territory):
        
        reinforcements = territory_info[stored_territory].troops - 1
        if reinforcements >= int(self._entry_text):
            self.__transfer(territory_info,last_clicked_territory,stored_territory)
            window.delete_interface("end reinforce")
            game.set_attribute("last clicked territory","")
            self.delete()
            game.switch_turn()

    def __transfer(self,territory_info,last_clicked_territory,stored_territory):
        territory_info[last_clicked_territory].troops += int(self._entry_text)
        window.find_interface("game elements").update_count(last_clicked_territory)
        territory_info[stored_territory].troops -= int(self._entry_text)
        window.find_interface("game elements").update_count(stored_territory)
                    
class Text():
    
    def __init__(self,text_,pos,font,colour,size):
        
        self.__text = text_
        self.__font = pygame.font.SysFont(font,size)
        self.__colour = colour
        self.__pos = pos
        self.__surf = self.__font.render(self.__text,True,self.__colour)
    
    def get_attribute(self,attribute):

        if attribute == "text":
            return self.__text
        elif attribute == "font":
            return self.__font
        elif attribute == "colour":
            return self.__colour
        elif attribute == "surf":
            return self.__surf
        elif attribute == "pos":
            return self.__pos

    def set_attribute(self,attribute,new):

        if attribute == "surf":
            self.__surf = new
        elif attribute == "text":
            self.__text = new
        elif attribute == "pos":
            self.__pos = new

class Card():
    
    def __init__(self,type_):

        self.__type = type_
        self.__pos = (10,10)
        try:
            self.__surf = pygame.image.load("IMAGES/" + self.__type + ".png").convert()
        except:
            pygame.quit()
            sys.exit("Error loading card image file(s)")
        self.__surf.set_colorkey((main.colours["BLACK"]),pygame.RLEACCEL)
        self.__rect = self.__surf.get_rect(topleft = self.__pos)

    def update(self):

        window.screen.blit(self.__surf,self.__pos)

    def get_attribute(self,attribute):

        if attribute == "type":
            return self.__type

    def set_attribute(self,attribute,new):

        if attribute == "pos":
            self.__pos = new

class Territory():

    def __init__(self,xpos,ypos,length):

        self.__surf = pygame.Surface((length,length),pygame.SRCALPHA)
        self.__rect = self.__surf.get_rect(topleft=(xpos,ypos))
        self.__name = ""
        self.__draw_top = False
        self.__draw_right = False
        self.__draw_bottom = False
        self.__draw_left = False

    def create_bounds(self):

        for territory in game.get_attribute("territories"):

            rect = territory.get_attribute("rect")
            name = territory.get_attribute("name")

            if self.__rect.collidepoint(rect.centerx, rect.bottom + 5) and self.__name != name:
                self.__draw_top = True
                
            if self.__rect.collidepoint(rect.left - 5, rect.centery) and self.__name != name:
                self.__draw_right = True
                
            if self.__rect.collidepoint(rect.centerx, rect.top - 5) and self.__name != name:
                self.__draw_bottom = True
            
            if self.__rect.collidepoint(rect.right + 5, rect.centery) and self.__name != name:
                self.__draw_left = True
    

    def update(self): 
        
        self.__surf.fill(game.get_territory_info()[self.__name].colour)

        if self.__rect.collidepoint(main.get_attribute("mouse pos")) and main.get_attribute("left mouse up"):

            if game.get_attribute("clicked territory") == "" and self.__name != "Ocean":
                window.update_info_box(1,game.get_attribute("current player").ID + " clicked " + self.__name)
                window.update_info_box(2,"")
                game.set_attribute("clicked territory",self.__name)
                
            main.unclick()

    def draw_lines(self):

        screen = window.screen

        if self.__draw_top:
            pygame.draw.line(screen,main.colours["BLACK"],self.__rect.topleft,self.__rect.topright)

        if self.__draw_right:
            pygame.draw.line(screen,main.colours["BLACK"],self.__rect.topright,self.__rect.bottomright)

        if self.__draw_bottom:
            pygame.draw.line(screen,main.colours["BLACK"],self.__rect.bottomright,self.__rect.bottomleft)

        if self.__draw_left:
            pygame.draw.line(screen,main.colours["BLACK"],self.__rect.bottomleft,self.__rect.topleft)

    def get_attribute(self,attribute):

        if attribute == "surf":
            return self.__surf
        elif attribute == "rect":
            return self.__rect
        elif attribute == "name":
            return self.__name

    def set_attribute(self,attribute,new):

        if attribute == "name":
            self.__name = new

class Dice():
    
    def __init__(self,colour,pos):

        game.add_to_array("dice",self)
        if colour == main.colours["RED"]:
            game.add_to_array("red dice",self)
        if colour == main.colours["WHITE"]:
            game.add_to_array("white dice",self)

        self.__num = 1
        self.__colour = colour
        self.__used = False
        self.__pos = pos
        self.__surf = pygame.Surface((40,40))
        self.__rect = self.__surf.get_rect(topleft = self.__pos)    

    def roll(self):

        self.__num = randint(1,6)

    def update(self):
            
        self.__surf.fill(self.__colour)
        
        positions = [[(20,20)],[(10,20),(30,20)],[(30,30),(20,20),(10,10)],
                     [(10,10),(10,30),(30,10),(30,30)],[(10,10),(10,30),(30,10),(30,30),(20,20)],
                     [(10,10),(10,20),(10,30),(30,10),(30,20),(30,30)]]
        
        for pos in positions[self.__num - 1]:
            pygame.draw.circle(self.__surf,main.colours["BLACK"],pos,5)

        window.screen.blit(self.__surf,self.__rect)

    def delete(self):

        if self.__colour == main.colours["RED"]:
            game.remove_from_array("red dice",self)
            
        if self.__colour == main.colours["WHITE"]:
            game.remove_from_array("white dice",self)

        game.remove_from_array("dice",self)
        del self


    def get_attribute(self,attribute):

        if attribute == "num":
            return self.__num
        elif attribute == "used":
            return self.__used

    def set_attribute(self,attribute,new):

        if attribute == "used":
            self.__used = new
        
class Map():

    def __init__(self):

        try:
            self.__map = open("ALL NATIONS MAP.txt","r")
            self.__text_map = self.__map.read().split(",")
            self.__territory_names = json.load(open("JSON files/territory names.JSON"))
            self.__adjacency_dict = json.load(open("JSON files/adjacency.JSON"))
            self.__continents = json.load(open("JSON files/continents.JSON"))
        except:
            pygame.quit()
            sys.exit("Error loading file(s)")
        
        self.__connection_positions = [[(1001,229),(1060,194)],[(140,194),(160,186)],[(381,172),(340,166)],[(381,172),(340,219)],[(381,172),(364,219)],[(401,408),(479,415)],
                                       [(520,239),(581,263)],[(520,239),(560,215)],[(511,221),(503,200)],[(524,280),(526,301)],[(639,519),(621,518)],[(639,519),(640,480)],
                                       [(962,319),(940,266)],[(962,319),(941,328)],[(869,460),(866,480)],[(881,489),(901,469)],[(881,489),(901,509)],[(917,479),(906,499)],
                                       [(917,479),(938,500)],[(481,181),(460,174)]]

        self.__territory_info = {"Greenland":InfoObject(main.colours["GREY"],[],0,None,None),"Northwest Territory":InfoObject(main.colours["GREY"],[],0,None,None),"Alaska":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Alberta":InfoObject(main.colours["GREY"],[],0,None,None),"Ontairo":InfoObject(main.colours["GREY"],[],0,None,None),"Quebec":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Western US":InfoObject(main.colours["GREY"],[],0,None,None),"Eastern US":InfoObject(main.colours["GREY"],[],0,None,None),"Central America":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Venezuela":InfoObject(main.colours["GREY"],[],0,None,None),"Peru":InfoObject(main.colours["GREY"],[],0,None,None),"Brazil":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Argentina":InfoObject(main.colours["GREY"],[],0,None,None),"Iceland":InfoObject(main.colours["GREY"],[],0,None,None),"Britain":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "North Africa":InfoObject(main.colours["GREY"],[],0,None,None),"Egypt":InfoObject(main.colours["GREY"],[],0,None,None),"East Africa":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Congo":InfoObject(main.colours["GREY"],[],0,None,None),"South Africa":InfoObject(main.colours["GREY"],[],0,None,None),"Madagascar":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Western Europe":InfoObject(main.colours["GREY"],[],0,None,None),"Northern Europe":InfoObject(main.colours["GREY"],[],0,None,None),"Southern Europe":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Ukraine":InfoObject(main.colours["GREY"],[],0,None,None),"Scandinavia":InfoObject(main.colours["GREY"],[],0,None,None),"Middle East":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "India":InfoObject(main.colours["GREY"],[],0,None,None),"Afghanistan":InfoObject(main.colours["GREY"],[],0,None,None),"Ural":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Siberia":InfoObject(main.colours["GREY"],[],0,None,None),"Yakursk":InfoObject(main.colours["GREY"],[],0,None,None),"Irkutsk":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Kamchatka":InfoObject(main.colours["GREY"],[],0,None,None),"Japan":InfoObject(main.colours["GREY"],[],0,None,None),"Mongolia":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "China":InfoObject(main.colours["GREY"],[],0,None,None),"Siam":InfoObject(main.colours["GREY"],[],0,None,None),"Indonesia":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "New Guinea":InfoObject(main.colours["GREY"],[],0,None,None),"Western Australia":InfoObject(main.colours["GREY"],[],0,None,None),"Eastern Australia":InfoObject(main.colours["GREY"],[],0,None,None),
                                 "Ocean":InfoObject(main.colours["OCEAN BLUE"],[],0,None,None)}

    def occupy_territory(self,new_occupant,territory):

        occupant = self.__territory_info[territory].occupant

        if occupant != None:    
            occupant.remove_from_array("occupied territories",territory)
        else:
            self.__territory_info[territory].troops = new_occupant.distribute_troop()
            
        self.__territory_info[territory].occupant = new_occupant
        self.__territory_info[territory].colour = new_occupant.get_attribute("colour")
        new_occupant.add_to_array("occupied territories",territory)
        for continent in self.__continents:
            game.get_attribute("current player").check_if_continent_held(continent)
            
        window.update_info_box(0,game.get_attribute("current player").ID + " holds " + str(len(game.get_attribute("current player").get_attribute("occupied territories"))) +
                               " territories and " + str(len(game.get_attribute("current player").get_attribute("occupied continents"))) + " continents")
        window.update_info_box(1,new_occupant.ID + " occupied " + territory)

    def get_attribute(self,attribute):

        if attribute == "territory names":
            return self.__territory_names
        elif attribute == "text map":
            return self.__text_map
        elif attribute == "adjacency dict":
            return self.__adjacency_dict
        elif attribute == "territory info":
            return self.__territory_info
        elif attribute == "continents":
            return self.__continents
        elif attribute == "connection positions":
            return self.__connection_positions

class InfoObject():

    def __init__(self,colour,array,troops,occupant,troop_count):
        
        self.colour = colour
        self.territory_array = array
        self.troops = troops
        self.occupant = occupant
        self.troop_count = troop_count

if __name__ == "__main__":
    call_main()
    
pygame.quit()
