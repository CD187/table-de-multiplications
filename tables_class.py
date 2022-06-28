#!/usr/bin/python3

import sys
from random import randint
from termios import *
from string import ascii_letters, digits
from time import time, asctime, sleep
import os 
from collections import defaultdict
        
class Game:
    def __init__(self):
        self.log_dir()
        self.max_trial = 30         # hard-coded value which defines number of trial in a game

    def log_dir(self):
        main_dir = './table_de_multiplication'
        path_log = main_dir + '/.logs'
        try:
            self.users = os.listdir(path_log)
        except FileNotFoundError:
            if os.path.isdir(main_dir) == True:
                os.mkdir(path_log,0o777)
            else:
                os.mkdir(main_dir,0o777)
                os.mkdir(path_log,0o777)
        self.players = os.listdir(path_log)
        self.path_log = path_log
               
    def random_question(self):
        mini=2
        maxi=9
        x= randint(mini,maxi)
        y= randint(mini,maxi)
        res = x*y
        return x, y, res 

    def weakness_question(self):
        weakness = self.weakness()
        i = randint(0, len(weakness)-1)
        mini=2
        maxi=9
        x= int(weakness[i])
        y= randint(mini,maxi)
        res = x*y
        return x, y, res
    
    def trial(self):
        with open(f'{self.path_log}/{self.player_name}', 'r') as file:
            lines = list(file)
            lines.reverse()
            for line in lines:
                if len(data := line.split()) == 5:      #5 refers to self.play()
                    if (trial := int(data[0])) > 0:  
                        return trial
                    break
            return self.max_trial          

                   
#creates counting dictionnary for each pair of operands (8 3 : (right, wrong) ...)  
#this function return this dictionnary as attribute and return a second attribute which is a list of each primary operands.
    def dict_maker(self):          
        with open(f'{self.path_log}/{self.player_name}', 'r') as file:
            lines = list(file)
            general_dict=defaultdict(lambda : (0,0)
            primary_operand = list() 
            for line in lines:
                if len(values := line.split()) == 5:       #5 refers to self.play()
                    right, wrong = general_dict[f'{values[1]} {values[2]}'] 
                    if values[3] == values[4]:             #if player's answer = right result
                        right += 1
                    else :
                        wrong += 1
                    general_dict[f'{values[1]} {values[2]}'] = (right, wrong)     
                    if values[1] not in primary_operand:
                        primary_operand.append(values[1])
            primary_operand.sort()
            self.general_dict = general_dict
            self.primary_operand = primary_operand 

#creates a dictionnary with key = 'primary operand' and value = average
    def by_operand_average(self):
        by_operand_dict = defaultdict(lambda : (0,0))
        for number in self.primary_operand:
            for key,value in self.general_dict.items():
                if k.startswith(number):
                right, wrong = value
                r,w = by_operand_dict[number]
                r = r + right
                w = w + wrong
                by_operand_dict[number]=(r,w) 
            right, wrong = by_operand_dict[number]
            by_operand_average[number]= round(right / (right + wrong) * 20, 2)
        self.by_op_average = by_operand_average

    def general_average(self):
        try:
            total_r = sum(value[0] for value in self.general_right_dict.values())
            total_w = sum(value[1] for value in self.general_wrong_dict.values())
            return round(total_r / (total_r + total_w) * 20, 2)
        except:
            return None     #if new player, ZeroDivisionError 

    def weakness(self):
        try:
            min_v = min(self.by_op_average.values())
            if min_v != 20:
                player_weakness = [k for k,v in self.by_op_average.items() if v == min_v]
                return player_weakness
            return None
        except:
            return None     #if new player, value error because min() arg is an empty sequence

    def last_trial_average(self):
        with open(f'{self.path_log}/{self.player_name}', 'r') as file:
            lines = list(file)
            lines.reverse()
            right = wrong = 0 
            try:
                trial = 0 
                for line in lines:
                    if trial == self.max_trial:
                        break
                    if line.startswith(str(trial)):
                        if (values:=line.split())[3] == values[4]:
                            right += 1
                        else:
                            wrong += 1
                        trial += 1
                return round(right / (right + wrong)* 20, 2)                
            except:
                return None     #if new player : ZeroDivisionError 


    def menu_select_player(self) : raise NotImplemented    
    def menu_player(self) : raise NotImplemented            #make player select a mode : play / statistics
    def play(self) : raise NotImplemented                   #play a game
    def statistics(self) : raise NotImplemented
    def timeout(self) : raise NotImplemented
    def wrong_answer(self): raise NotImplemented
    def right_answer(self): raise NotImplemented


class TUI_Linux(Game):
    def _visit_stdin(self):
        old_mode = tcgetattr(sys.stdin)
        try:
            IFLAG = 0
            OFLAG = 1
            CFLAG = 2
            LFLAG = 3
            ISPEED = 4
            OSPEED = 5
            CC = 6

            mode = old_mode[:]
            mode[IFLAG] = mode[IFLAG] & ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON)
            mode[OFLAG] = mode[OFLAG] & ~(OPOST)
            mode[CFLAG] = mode[CFLAG] & ~(CSIZE | PARENB)
            mode[CFLAG] = mode[CFLAG] | (CS8)
            mode[LFLAG] = mode[LFLAG] & ~(ECHO | ICANON | IEXTEN | ISIG)
            mode[CC][VMIN] = 0
            mode[CC][VTIME] = 1
            
            esc_mode = mode[:]
            esc_mode[CC][VTIME] = 0
            tcsetattr(sys.stdin,TCSAFLUSH,mode)
            while True:
                ret = sys.stdin.read(1)
                if ret == '\x1b':
                    tcsetattr(sys.stdin, TCSAFLUSH, esc_mode)
                    esc_seq = sys.stdin.read()
                    if esc_seq:
                        ret += esc_seq
                    tcsetattr(sys.stdin, TCSAFLUSH, mode)
                elif ret == '\x03':     
                    raise KeyboardInterrupt
                yield ret
        finally:
            tcsetattr(sys.stdin, TCSAFLUSH, old_mode)
 
# _custom_input() returns a string, and takes 2 parameters : the valid chars and the way to valid the input. 
# We can give some options prompt = 'my_string' / time = (give an integer for 'X' seconds)  / backspace = 'disable' (to disable char deletion)

    def _custom_input(self,input_validation, valid_char, prompt = None, timer = None, backspace = None):
        if timer and timer > 0:
                    starting_time = time()
        if backspace and  backspace.lower() != 'disable':
            raise ValueError 
        char = user_input = ''
        iterator = self._visit_stdin()
        while not input_validation(user_input):
            if timer and time() - starting_time > timer:
                raise ValueError 
            char = next(iterator)
            if valid_char(char):
                user_input += char
            elif char == '\x7f'  or char == '\x08':
                if not backspace:
                    user_input = user_input[:-1]
            print('\x1b[2K', end='')
            if prompt:
                print(prompt, user_input, end='\r')
            else:
                print(user_input, end='\r')
        return user_input

    def menu_select_player(self):
        os.system('clear')
        sys.stdout.write('\x1b[?25l') #hide cursor 
        print('choix du joueur :','\n')
        for player in self.players:
            print('\x1b[32m' + player + '\x1b[37m')
        print('\necris \x1b[32mnouveau\x1b[37m pour créer un nouveau joueur, sinon ecris ton pseudo :\n')
        player_name = self._custom_input(lambda user_input : user_input in [*self.players, 'nouveau'],
                                         lambda char : char in [*ascii_letters, *digits],
                                         prompt='pseudo :')
        if player_name == 'nouveau':
            os.system('clear')
            while player_name == 'nouveau' or player_name == '':
                player_name = self._custom_input(lambda user_input : True if user_input.endswith('\x0d') else False,
                                                 lambda char : True if char in [*ascii_letters, *digits, '\x0d'] else False,
                                                 prompt = 'pseudo :')
            player_name = player_name[:-1]
            with open(self.path_log+f'/{player_name}', 'a') as file:
                file.write(player_name + '\n')
        self.player_name = player_name

    def menu_player(self):
        os.system('clear')
        welcome = f'bienvenue {self.player_name}' 
        i = 0 
        while i != len(welcome) + 1:
            print('\x1b[2K', end='')
            print(welcome[:i], end ='\r')
            i += 1
            sleep(0.05)
        sleep(1)
        print('\n\n\n')
        print('Pour voir tes statistique appuie sur la touche ---> S')
        print('pour jouer appuie sur la touche ---> entrée')
        print('pour changer de joueur appuie sur la touche ---> retour')
        print("\n\n\nA n'importe quel moment tu peux quitter en appuyant sur ---> ctrl + C")
        valid_touch = ['\x0d' , 's' , 'S' , '\x7f' , '\x08']
        selection = self._custom_input(lambda user_input : True if user_input else False,
                                       lambda char : True if char in valid_touch else False)
        if selection == '\x0d':
            return 1
        elif selection == 's' or selection =='S':
            return 0
        elif selection == '\x7f' or selection == '\x08':
            return -1
    
    def player_statistics(self):
        os.system('clear')
        self.dict_maker()
        self.by_operand_average()
        a = self.general_average()
        b = self.last_trial_average()
        def colorized_average(number):
            if number < 10:
                typed_color = '\x1b[31m'
            elif 10 <= number < 15:
                typed_color = '\x1b[33m'
            elif 15 <= number <= 20:
                typed_color = '\x1b[32m'
            old_mode = '\x1b[37m'
            string = f"{typed_color}{number}{old_mode}" 
            return string
        if b: 
            A = colorized_average(a)
            B = colorized_average(b)
            print(f"ta moyenne generale est de : {A}\n\n") 
            print(f"le score de ta dernière partie est : {B}\n\n") 
            print(f"Ta moyenne pour chaque table est de :\n")
            for k,v in self.by_op_average.items():
                V = colorized_average(v)
                print(    f"Table de {k} : {V}")
            weakness = self.weakness()
            if weakness == None:
                print("Bravo ! pour le moment c'est un sans faute !\n\n") 
            elif len(weakness) == 1:
                x = ''.join(weakness)
                print(f"\n\nil va falloir réviser ta table de {x}\n\n")
            else:
                x = ', '.join(weakness[:-1]) + ' et ' + str(weakness[-1])
                print(f"\n\nil va falloir réviser tes tables de {x}\n\n")
        else:
            print('aucune moyenne ne peut être établie pour le moment, joue au moins une partie complète.\n\n')
        back = self._custom_input(lambda prop : True if prop.startswith('\x0d') else False,
                                  lambda char : True if char == '\x0d' else False,
                                  prompt = 'Appuie sur entrée pour revenir au menu précédent')

    def play(self):
        os.system('clear')
        trial = self.trial()
        weakness = self.weakness()
        with open(self.path_log+f'/{self.player_name}', 'a') as file:
            file.write('\n'+ 'start ' +  asctime())
            while trial != 0 :
                if weakness:                                        #
                    if trial % 3 == 0:                              # 
                        x, y, result = self.weakness_question()     # this part is a way to work on player's weakness
                    else:                                           # 30% of questions are based on his.
                        x, y, result = self.random_question()       # 
                else:                                               # 
                    x, y, result = self.random_question()           #

                no_value = True
                try:
                    while no_value == True:
                        user_prop = self._custom_input(lambda  prop : True if prop.endswith('\x0d') else False,
                                                       lambda char : True if char in [*digits, '\x0d']  else False,
                                                       prompt = f'\x1b[32m{trial}\x1b[37m    {x} x {y} =', timer = 10)   
                        if user_prop != '\x0d':
                            no_value = False
                    user_prop = user_prop[:-1]
                    if user_prop == '':
                        self.wrong_answer(x, y, result)
                    elif int(user_prop) != int(result):
                        self.wrong_answer(x, y, result)
                    else :
                        self.right_answer()
                except ValueError:
                    self.timeout(x, y, result)
                    user_prop = 'TIMEOUT'
                trial -= 1 
                values = f'{trial} {x} {y} {result} {user_prop}'
                file.write('\n' + values)  

    def timeout(self, operand_1, operand_2, result):
        print(f"\nle temps est écoulé ... {operand_1} x {operand_2} = {result}")

    def wrong_answer(self, operand_1, operand_2, result):
        print(f"\nmauvaise réponse ... {operand_1} x {operand_2} = {result}")

    def right_answer(self):
        print('\nbonne réponse !')

class GUI_tk(Game):
    pass

class TUI_Windows(Game):
    pass


if __name__ == '__main__':
    #try:
    #    import tkinter as tk
    #    launch = GUI_tk()
    #except ImportError:
    #    plat = sys.platform
    #    if plat == 'linux':
    #        launch = TUI_Linux()
    #    elif plat == 'win32':
    #        launch = TUI_Windows()
    #    else:
    #        raise RuntimeError('Sorry Lin or Win32 only')

    launch = TUI_Linux()  

    while True:
        launch.menu_select_player()
        launch.dict_maker()
        launch.by_operand_average()
        change_player = False
        while change_player == False:
            choice = launch.menu_player()
            if choice == -1:
                change_player == True
            elif choice == 0:
                launch.player_statistics()
            elif choice == 1:
                launch.play()
