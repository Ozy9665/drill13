from pico2d import *
import random
import game_world
import game_framework

# 체력 표시 -> 시간 표시하듯 표시, and 체력바를 시작점 + 체력만큼의 거리를 네모블럭 표시

# Bird Action Speed
TIMER_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIMER_PER_ACTION
FRAMES_PER_ACTION = 8

# Bird Flying Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30cm
FLYING_SPEED_KMPH = 45.0   # Km / Hour
FLYING_SPEED_MPM = (FLYING_SPEED_KMPH * 1000.0 / 60.0)
FLYING_SPEED_MPS = (FLYING_SPEED_MPM / 60.0)
FLYING_SPEED_PPS = (FLYING_SPEED_MPS * PIXEL_PER_METER)


# 1 : 이벤트 정의
RD, LD, RU, LU, TIMER, SPACE = range(6)
event_name = ['RD', 'LD', 'RU', 'LU', 'TIMER', 'SPACE']

key_event_table = {
    (SDL_KEYDOWN, SDLK_SPACE): SPACE,
    (SDL_KEYDOWN, SDLK_RIGHT): RD,
    (SDL_KEYDOWN, SDLK_LEFT): LD,
    (SDL_KEYUP, SDLK_RIGHT): RU,
    (SDL_KEYUP, SDLK_LEFT): LU
}


#2 : 상태의 정의
class FLYING:
    @staticmethod
    def enter(self, event):
        print('ENTER IDLE')
        self.dir = 1
        self.timer = 1000

    @staticmethod
    def exit(self, event):
        print('EXIT IDLE')
        if event == SPACE:
            self.fire_ball()

    @staticmethod
    def do(self):       # 좌우 비행
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 5
        self.x += self.dir * FLYING_SPEED_PPS * game_framework.frame_time
        self.x = clamp(0, self.x, 1500)
        if self.x == 1500:
            self.dir = -1
        elif self.x == 0:
            self.dir = 1


    @staticmethod
    def draw(self):
        if self.dir == 1:
            self.image.clip_draw(int(self.frame) * 180, 344, 180, 172, self.x, self.y, 110, 50)
        else:
            self.image.clip_composite_draw(int(self.frame) * 180, 172, 180, 172, 0, 'h', self.x, self.y, 110, 50)


class RUN:
    def enter(self, event):
        print('ENTER RUN')
        if event == RD:
            self.dir += 1
        elif event == LD:
            self.dir -= 1
        elif event == RU:
            self.dir -= 1
        elif event == LU:
            self.dir += 1

    def exit(self, event):
        print('EXIT RUN')
        self.face_dir = self.dir
        if event == SPACE:
            self.fire_ball()

    def do(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.x += self.dir * FLYING_SPEED_PPS * game_framework.frame_time
        self.x = clamp(0, self.x, 1600)

    def draw(self):
        if self.dir == -1:
            self.image.clip_draw(int(self.frame)*100, 0, 170, 100, self.x, self.y)
        elif self.dir == 1:
            self.image.clip_draw(int(self.frame)*100, 100, 170, 100, self.x, self.y)


class SLEEP:

    def enter(self, event):
        print('ENTER SLEEP')
        self.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.face_dir == -1:
            self.image.clip_composite_draw(self.frame * 100, 200, 100, 100,
                                          -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)
        else:
            self.image.clip_composite_draw(self.frame * 100, 300, 100, 100,
                                          3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)


#3. 상태 변환 구현

next_state = {
    FLYING:  {},
}


class Bird:

    def __init__(self):
        self.x, self.y = random.randint(100, 1300), random.randint(120, 400)
        self.frame = 0
        self.dir, self.face_dir = 1, 1
        self.image = load_image('bird_animation.png')
        # self.font = load_font('ENCR10B.TTF', 16)

        self.timer = 100

        self.event_que = []
        self.cur_state = FLYING
        self.cur_state.enter(self, None)

    def update(self):
        self.cur_state.do(self)

        if self.event_que:
            event = self.event_que.pop()
            self.cur_state.exit(self, event)
            try:
                self.cur_state = next_state[self.cur_state][event]
            except KeyError:
                print(f'ERROR: State {self.cur_state.__name__}    Event {event_name[event]}')
            self.cur_state.enter(self, event)

    def draw(self):
        self.cur_state.draw(self)
        # self.font.draw(self.x - 60, self.y + 50, f'(Time: {get_time():.2f})', (255, 255, 0))

    def add_event(self, event):
        self.event_que.insert(0, event)

    def handle_event(self, event):
        if (event.type, event.key) in key_event_table:
            key_event = key_event_table[(event.type, event.key)]
            self.add_event(key_event)

