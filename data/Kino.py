from dataclasses import dataclass
from dataclasses_json import dataclass_json
from json import loads, dumps
from typing import TypedDict

class KinoDict(TypedDict, total=False):
    number:int
    name:str
    episodeCounts:list
    episodeTimes:list
    isWatched:bool


def make_kino_dict(number:int, name:str, episodeCounts:list, episodeTimes:list, isWatched:bool = False) -> KinoDict:
    """Собирает словарь фильма для KinosHandler: номера и серии — целые числа."""
    return {
        'number': int(number),
        'name': str(name).strip(),
        'episodeCounts': [int(count) for count in episodeCounts],
        'episodeTimes': [int(time) for time in episodeTimes],
        'isWatched': bool(isWatched),
    }
    
@dataclass_json
@dataclass
class Kino:
    number:int
    name:str
    episodeCounts:list
    episodeTimes:list
    isWatched:bool = False
    
    def __post_init__(self):
        self.seasonCount = len(self.episodeCounts)
        self.totalTime = sum(self.episodeCounts[i] * self.episodeTimes[i] for i in range(self.seasonCount)) / 60
        
    def __lt__(self, other):
        return self.number < other.number
    
    
class KinosHandler():
    
    def __init__(self, json:str=None, kinos:list[Kino]=None) -> None:
        if json:
            self.Kinos = [Kino.from_json(item) for item in loads(json)]
        elif kinos:
            self.Kinos = kinos
        else:
            self.Kinos = []
    
    def getTypedKinos(self, isWatched:bool):
        return [kino for kino in self.Kinos if kino.isWatched == isWatched]    
    
    def setWatched(self, kino:Kino):
        kino.isWatched = True
        if kino.number == 1:
             self.shiftToFirst(self.getTypedKinos(False))
        else: self.shift(self.getTypedKinos(False))
        
    def setWatching(self, kino:Kino):
        kinos = self.getTypedKinos(False)
        
        if kinos:
            lastNumber = kinos[-1].number
        else:
            lastNumber = 0
        number =  kino.number
        if number > lastNumber:
            kino.number = lastNumber + 1
        elif number in [kino.number for kino in kinos]:
            for k in kinos:
                if k.number >= number: k.number += 1
                
        kino.isWatched = False
    
    def toJson(self) -> str:
        return dumps([kino.to_json() for kino in self.Kinos])
    
    def __repr__(self) -> str:
        return '\n'.join([kino.__repr__() for kino in self.Kinos])
    
    def newNumberToAdd(self, dic:KinoDict):
        if self.Kinos:
            lastNumber = self.Kinos[-1].number
        else:
            lastNumber = 0
        number =  dic['number']
        if number > lastNumber:
            dic['number'] = lastNumber + 1
        elif number in [kino.number for kino in self.Kinos]:
            for kino in self.Kinos:
                if kino.number >= number: kino.number += 1
                
    def newNumberToChange(self, dic:KinoDict, prevNumber:int):
        if dic['number'] > len(self.Kinos): dic['number'] = len(self.Kinos)
        curNumber = dic['number']
        if curNumber < prevNumber:
            for kino in self.Kinos:
                if prevNumber >= kino.number >= curNumber: 
                    kino.number += 1
        elif curNumber > prevNumber:
            for kino in self.Kinos:
                if curNumber >= kino.number >= prevNumber: 
                    kino.number -= 1
    
    def append(self, dic:KinoDict):
        self.newNumberToAdd(dic)
        kino = Kino.from_dict(dic)
        self.Kinos.append(kino)
        self.Kinos.sort(key=lambda obj: obj.number)
        return kino
    
    def removeAt(self, index:int):
        self.Kinos.pop(index)
        self.shift()
        
    def remove(self, kino:Kino) -> int:
        if kino in self.Kinos:
            self.Kinos.remove(kino)
            if kino.number == 1:
                return self.shiftToFirst(self.getTypedKinos(False))
            return self.shift(self.getTypedKinos(False))
        
    def update(self, prevKino:Kino, dic:KinoDict):
        self.newNumberToChange(dic, prevKino.number)
        kino = Kino.from_dict(dic)
        index = self.Kinos.index(prevKino)
        self.Kinos[index] = kino
        self.Kinos.sort(key=lambda obj: obj.number)
        return kino
    
    def clear(self):
        self.Kinos.clear()
        
    def shiftToFirst(self, kinos):
        for kino in kinos:
            kino.number -= 1
        return 0
        
    def shift(self, kinos):
        number = -1
        for kino1, kino2 in zip(kinos, kinos[1:]):
            if kino2.number - kino1.number == 2:
                number += kino2.number - 1
        
        if number != -1:
            for kino in kinos[number:]:
                kino.number -= 1
        
        return number
