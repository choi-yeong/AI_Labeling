import random

class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.attack = 20
        self.location = "start_room"
        self.inventory = []

    def move(self, room):
        self.location = room
        print(f"{self.name}이(가) {room}으로 이동했습니다.")

    def attack_monster(self, monster):
        damage = random.randint(10, self.attack)
        monster.hp -= damage
        print(f"{self.name}이(가) {monster.name}에게 {damage}의 데미지를 입혔습니다!")
        if monster.hp <= 0:
            print(f"{monster.name}을(를) 쓰러뜨렸습니다!")
            return True
        return False

class Monster:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack

    def attack_player(self, player):
        damage = random.randint(5, self.attack)
        player.hp -= damage
        print(f"{self.name}이(가) {player.name}에게 {damage}의 데미지를 입혔습니다!")
        if player.hp <= 0:
            print(f"{player.name}이(가) 죽었습니다!")
            return True
        return False

class Room:
    def __init__(self, name, monster=None, item=None):
        self.name = name
        self.monster = monster
        self.item = item

    def describe(self):
        print(f"현재 위치: {self.name}")
        if self.monster:
            print(f"주의! {self.monster.name}이(가) 있습니다!")
        if self.item:
            print(f"아이템 발견: {self.item}")

class Game:
    def __init__(self):
        self.player = Player("Hero")
        self.rooms = {
            "start_room": Room("시작 방"),
            "monster_room": Room("몬스터 방", Monster("슬라임", 50, 15)),
            "treasure_room": Room("보물 방", item="마법의 검")
        }

    def play(self):
        print(f"환영합니다, {self.player.name}!")
        while self.player.hp > 0:
            current_room = self.rooms[self.player.location]
            current_room.describe()

            action = input("무엇을 하시겠습니까? (1: 이동, 2: 공격, 3: 종료): ")
            if action == "1":
                new_room = input("어디로 이동하시겠습니까? (monster_room, treasure_room): ")
                if new_room in self.rooms:
                    self.player.move(new_room)
            elif action == "2" and current_room.monster:
                if self.player.attack_monster(current_room.monster):
                    current_room.monster = None  # 몬스터 제거
            elif action == "3":
                print("게임을 종료합니다.")
                break
            else:
                print("잘못된 입력입니다!")

            if current_room.monster:
                if current_room.monster.attack_player(self.player):
                    break

            if self.player.hp <= 0:
                print("게임 오버!")
                break

if __name__ == "__main__":
    game = Game()
    game.play()