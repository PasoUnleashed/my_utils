import my_utils
from my_utils import games
import random
class XOState(games.TurnGameGamestate):
    def __init__(self,size):
        super().__init__()
        self.size=size
        self.board = [[0 for i in range(size)] for j in range(size)]
    @classmethod
    def get_start_state(cls):
        ret =XOState(3)
        return ret
    def get_children(self):
        ret = []
        if(self.evaluate_status()!=None):
            return []
        for i in range(self.size):
            for j in range(self.size):
                if(self.board[i][j]==0):
                    ch = self.copy()
                    ch.board[i][j]=self.current_player_id+1
                    ch.current_player_id+=1
                    ch.current_player_id%=2
                    ret.append(ch)
        return ret
    def draw_state(self,screen):
        pass
    def print_state(self):
        for i in self.board:
            for j in i:
                print(j,'|',end='')
            print()
    def evaluate_status(self):
        for i in self.board:
            if(len(set(i))==1 and i[0]!=0):
                return games.TurnBasedGameStatus(games.GameOverSignal.WIN,[i[0]])
        nb = zip(*self.board)  
        for i in nb:
            if(len(set(i))==1 and i[0]!=0):
                return games.TurnBasedGameStatus(games.GameOverSignal.WIN,[i[0]])
        start = self.board[0][0]
        start2 = self.board[-1][0]
        w = True
        w2= True
        for i in range(1,self.size):
            if(self.board[i][i]!=start):
                w = False
            if(self.board[i][-(i+1)]!=start2 ):
                w2=False
        if(w and start!=0):
            return games.TurnBasedGameStatus(games.GameOverSignal.WIN,[start])
        if(w2 and start2!=0):
            return games.TurnBasedGameStatus(games.GameOverSignal.WIN,[start2])
        nz= True
        for i in self.board:
            for j in i:
                if(j==0):
                    nz=False
        if(nz):
            return games.TurnBasedGameStatus(games.GameOverSignal.DRAW,[0,1])
    def __hash__(self):
        return hash("".join(["".join((str(j) for j in i)) for i in self.board]))
    def __eq__(self, other):
         return (
             self.__class__ == other.__class__ and
             self.__hash__()==other.__hash__() )
