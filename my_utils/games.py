from abc import ABC,abstractclassmethod,abstractmethod
from enum import Enum
from my_utils import util,compute
import copy
import random
class TurnBasedGame:
    def __init__(self,players,player_count,gamestate_type):
        for i in players:
            if not isinstance(i,TurnBasedPlayer):
                raise Exception(f"Non-player object passed to turn based game (got type {type(i)})")
        if(not issubclass(gamestate_type,TurnGameGamestate)):
            raise Exception(f"Got non TurnBasedGameState (got: {str(gamestate_type)}) type for arg gamestate_type")
        self.players = players
        self.player_count = player_count
        self.current_state = gamestate_type.get_start_state()
        self.is_over=False
    def turn(self):
        if(self.current_state.current_player_id>=len(self.players)):
            raise Exception(f'Player id out of range (Game initialized with {len(self.players)} players, current player id = {self.current_state.current_player_id} (P{self.current_state.current_player_id+1}))')
        player = self.players[self.current_state.current_player_id]
        options = self.current_state.get_children()

        choice = player.select_next_state(self.current_state,options,self.current_state.current_player_id)
        if(choice not in options):
            raise Exception(f'Player {self.current_state.current_player_id} picked a move not in the children list of the current state')
        self.current_state=choice
        status = self.current_state.evaluate_status()
        if(not status is None):
            self.is_over = True
            return status
    def run_to_end(self,verbose=False,visual=False):
        status = self.current_state.evaluate_status()
        while status is None:
            status = self.turn()
            if(verbose):
                self.current_state.print_state()
                print()
        if(verbose):
            print(status.signal,status.players)
        return status
class TurnGameGamestate(ABC):
    def __init__(self):
        self.current_player_id = 0
    @abstractclassmethod
    def get_start_state(cls):
        pass
    @abstractmethod
    def get_children(self):
        pass
    @abstractmethod
    def draw_state(self,screen):
        pass
    @abstractmethod
    def evaluate_status(self):
        pass
    @abstractmethod
    def print_state(self):
        pass
    def copy(self):
        return copy.deepcopy(self)
class GameOverSignal(Enum):
    WIN=1
    LOSE=2
    DRAW=3
    CANCELLED=4
class TurnBasedGameStatus:
    def __init__(self,signal,players):
        self.signal = signal
        self.players = players
class TurnBasedPlayer(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def select_next_state(self,current_state,choices,pid):
        pass
class MinMaxPlayer(TurnBasedPlayer):
    def __init__(self,heuristic,depth):
        super().__init__()
        self.heuristic = heuristic
        self.depth = depth
    def select_next_state(self,current_state,choices,pid):
        best_state = None
        best_eval = None
        for i in choices:
            ieval = self.minmax(i,current_state.current_player_id,pid)
            if(best_state is None or ieval>best_eval):
                best_state=i
                best_eval= ieval
        return best_state
    def minmax(self,state,current_player_id,pid,depth=None):
        if(depth is None):
            depth=self.depth
        if(depth==0):
            return self.heuristic(state,pid)
        best_state = None
        best_eval = None
        if(current_player_id==pid):
            eval_lambda =lambda x,y: x>y
        else:
            eval_lambda =lambda x,y: x<y
        for i in state.get_children():
            ieval = self.minmax(i,state.current_player_id,pid,depth-1)
            if( best_state is None or eval_lambda(best_eval,ieval) ):
                best_state = i
                best_eval = ieval
        return best_eval
        
class RandomTurnBasedPlayer(TurnBasedPlayer):
    def select_next_state(self,current_state,choices,pid):
        return random.choice(choices)