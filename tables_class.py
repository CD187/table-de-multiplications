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
        print('\x1b[37m')

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
                   
#creates two counting dictionnaries for each pair of operands (8 3 : 1,2 6 : 3,...) one for right answer, an other one for wrong. 
#this function return these 2 dictionnaries as attributes and return a third atribute which is a list of each primary operands.
    def dict_maker(self):          
        with open(f'{self.path_log}/{self.player_name}', 'r') as file:
            lines = list(file)

            right_dict = defaultdict(int)
            wrong_dict = defaultdict(int)
            primary_operand = list() 
            for line in lines:
                if len(values := line.split()) == 5:       #5 refers to self.play()
                    if values[3] == values[4]:
                        right_dict[f'{values[1]} {values[2]}'] += 1
                    else :
                        wrong_dict[f'{values[1]} {values[2]}'] += 1
                    if values[1] not in primary_operand:
                        primary_operand.append(values[1])
            primary_operand.sort()
            self.general_right_dict = right_dict
            self.general_wrong_dict = wrong_dict
            self.primary_operand = primary_operand 

#creates a dictionnary with key = 'primary operand' and value = average
    def by_operand_average(self):
        right_answer = defaultdict(int)
        wrong_answer = defaultdict(int)
        by_operand_average = defaultdict(int)
        for number in self.primary_operand:
            for k,total in self.general_right_dict.items():
                if k.startswith(number):
                    right_answer[number] += total 
            for k,total in self.general_wrong_dict.items():
                if k.startswith(number):
                    wrong_answer[number] += total 
            if (right := right_answer.get(number)) == None:     #in case all user's answers are falses or new player
                right = 0
            if (wrong := wrong_answer.get(number)) == None:     #in case all user's answers are rights or new player
                wrong = 0
            by_operand_average[number]= round(right / (right + wrong) * 20, 2)
        self.by_op_average = by_operand_average

    def general_average(self):
        try:
            total_r = sum(self.general_right_dict.values())
            total_w = sum(self.general_wrong_dict.values())
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
                return round(right / (right + wrong)* 20, 1)                
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
    def _visit_stdin(self):                 #thank you Nophke for this function !
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
 
    def _custom_input(self,input_validation, valid_char, prompt = None, timer = None, max_len = None, backspace = None, middle = None):
        if timer and timer > 0:
                    starting_time = time()
        if backspace and  backspace.lower() != 'disable':
            raise ValueError 
        char = user_input = ''
        iterator = self._visit_stdin()
        while not input_validation(user_input):            
            print('\x1b[2K', end='')
            if not middle:
                if prompt:
                    print(prompt, user_input, end='\r')
                else:
                    print(user_input, end='\r')
            else:
                if prompt:
                    print(self.middle_window(prompt + user_input), end='\r')
                else:
                    print(self.middle_window(user_input), end='\r')
            while True:              #this loop is done in order to avoid printing bug if we modify the terminal size 
                if timer and time() - starting_time > timer:
                    user_input += 'ValueError\x0d'
                    break
                char = next(iterator)
                if valid_char(char):
                    if not max_len or max_len and len(user_input) < max_len:
                        user_input += char
                        break
                elif char == '\x7f'  or char == '\x08':
                    if not backspace:
                        user_input = user_input[:-1]
                        break
        return user_input

    def menu_selector(self, list_of_string, size, prefixe, suffixe, prompt = None):
        i = 0
        keys = ['\x1b\x5b\x41','\x1b\x5b\x42', '\x0d']
        validation = False
        while True:
            os.system('clear')
            if prompt:
                print('\n', self.middle_window(prompt),'\n')
            max_lenght = len(list_of_string) 
            if i == max_lenght :
                i = 0
            elif i == -1:
                i = max_lenght - 1
            for index,element in enumerate(list_of_string):
                if index == i :
                    print(self.middle_window(element,size = size, prefixe = prefixe, suffixe = suffixe)) 
                else:
                    print(self.middle_window(element))
            while validation == False:
                char = self._custom_input(lambda ui : True if ui != '' else False,
                                          lambda char : True if char in keys else False)
                if char == '\x1b\x5b\x42':    #arrow down
                    i += 1
                    break
                elif char == '\x1b\x5b\x41':  #arrow up
                    i -= 1
                    break
                elif char == '\x0d':          #enter
                    validation = True
                    break
            if validation == True:
                choice = list_of_string[i]
                break               
        return choice
    
    def middle_window(self, string, size = None, prefixe = None, suffixe = None):
        col, lin = os.get_terminal_size()
        spaces = round((col - len(string) + self.len_esc_str(string)) / 2)
        if size and prefixe and suffixe:
            try:
                a = size - len(string)
                if a < 0:
                    raise ValueError
            except:
                pass
            colored_spaces = spaces - round((col-size) / 2)
            new_string = (spaces - colored_spaces) * ' ' + prefixe + colored_spaces * ' '+ string + (a - colored_spaces) * ' ' + suffixe
        else:
            new_string = spaces * ' ' + string
        return new_string
   
    def len_esc_str(self,string):
        counter = 0
        flag = 0
        for char in string:
            if char == '\x1b':
                flag = 1
            if flag == 1:
                counter += 1
            if flag == 1 and char == 'm':
                flag = 0
        return counter
    
    def _print_char_by_char(self, string, time, middle = None, clear = None, new_line = None):
        if clear:
            os.system('clear')
        if new_line:
            print()
        old_mode = tcgetattr(sys.stdin)
        new_mode = tcgetattr(sys.stdin)
        new_mode[3] = new_mode[3] & ~ECHO
        try:
            tcsetattr(sys.stdin,TCSADRAIN,new_mode)
            i = 1
            if middle : 
                string = ' ' + self.middle_window(string) # ' ' IS A HACK ! WE HAVE TO FIX IT ! (check middle_win)
                flag = 0
                for char in string:
                    if char == ' ': 
                        i += 1
                    if char == '\x1b':
                        flag = 1
                    if flag == 1:
                        i += 1
                    if flag == 1 and char == 'm':
                        break
            while i != len(string) + 1:
                print('\x1b[2k', end='')
                print(string[:i], end='\r')
                i += 1
                sleep(time)
        finally:
            tcsetattr(sys.stdin,TCSAFLUSH, old_mode)
        if new_line:
            print()

    def menu_select_player(self, title):
        sys.stdout.write('\x1b[?25l')                   #hide cursor 
        max_len_player_name = 16
        if len(self.players) < 9:                       #max 10 players
            self.players.append('nouveau joueur')
        player_name = self.menu_selector(self.players, 24, '\x1b[30;107m', '\x1b[0;1m', prompt = title)
        if player_name == 'nouveau joueur':
            os.system('clear')
            print(self.middle_window('entre ton pseudo :'), '\n\n\n')
            player_name = self._custom_input(lambda user_input : True if user_input.endswith('\x0d') else False,
                                             lambda char : True if char in [*ascii_letters, *digits, '\x0d'] else False,
                                             max_len = 16,
                                             middle = True)
            player_name = player_name[:-1]
            with open(self.path_log+f'/{player_name}', 'a') as file:
                file.write(player_name + '\n')
                self.players[-1] = player_name    
        else:
            self.players = self.players[:-1]
        self.player_name = player_name

    def menu_player(self, title):
        os.system('clear')
        menu = ['statistiques', 'jouer', 'changer de joueur']
        selection = self.menu_selector(menu, 24, '\x1b[30;107m', '\x1b[0;1m', prompt = title)
        print("\n\n\nA n'importe quel moment de la partie tu peux quitter en appuyant sur -> ctrl + C")
        if selection == 'statistiques':
            return 0
        elif selection == 'jouer':
            return 1
        elif selection == 'changer de joueur':
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
            self._print_char_by_char('STATISTIQUES :', 0.03,  middle = True, clear = True, new_line = True) 
            print()
            print(self.middle_window(f"ta moyenne generale est de : {A}")) 
            print(self.middle_window(f"le score de ta dernière partie est : {B}") + '\n') 
            print(self.middle_window(f"Ta moyenne pour chaque table est de :") + '\n')
            for k,v in self.by_op_average.items():
                V = colorized_average(v)
                print(self.middle_window(f"Table de {k} : {V}"))
            weakness = self.weakness()
            if weakness == None:
                print('\n\n' + self.middle_window("Bravo ! pour le moment c'est un sans faute !") +'\n\n') 
            elif len(weakness) == 1:
                x = ''.join(weakness)
                print('\n\n' + self.middle_window(f'il va falloir réviser ta table de {x}') + '\n\n')
            else:
                x = ', '.join(weakness[:-1]) + ' et ' + str(weakness[-1])
                print('\n\n' + self.middle_window(f"il va falloir réviser tes tables de {x}") + '\n\n')
        else:
            print(self.middle_window('aucune moyenne ne peut être établie pour le moment, joue au moins une partie complète.') + '\n\n')
        back = self._custom_input(lambda prop : True if prop.startswith('\x0d') else False,
                                  lambda char : True if char == '\x0d' else False,
                                  prompt = 'Appuie sur entrée pour revenir au menu précédent',
                                  middle = True)

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
                while no_value == True:
                    user_prop = self._custom_input(lambda  prop : True if prop.endswith('\x0d') else False,
                                                   lambda char : True if char in [*digits, '\x0d']  else False,
                                                   prompt = f'\x1b[32m{trial}\x1b[37m    {x} x {y} =', 
                                                   timer = 10)   
                    if user_prop != '\x0d':
                        no_value = False
                user_prop = user_prop[:-1]
                if user_prop == 'ValueError':
                    self.timeout(x, y, result)
                    user_prop = 'TIMEOUT'
                elif user_prop == '' or int(user_prop) != int(result):
                    self.wrong_answer(x, y, result)
                else:
                    self.right_answer()
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
        
        title = 'choix du joueur :'             #we could put titles into a dict ...
        launch._print_char_by_char(title, 0.03, middle = True, clear = True, new_line = True)
        launch.menu_select_player(title)
        launch.dict_maker()
        launch.by_operand_average()
        title = f'bienvenue {launch.player_name}' 
        launch._print_char_by_char(title, 0.03, middle = True, clear = True, new_line = True)
        while True:
            choice = launch.menu_player(title)
            if choice == -1:
                break
            elif choice == 0:
                launch.player_statistics()
            elif choice == 1:
                launch.play()
