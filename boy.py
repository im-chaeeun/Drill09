#2022182035 임채은
# 이것은 각 상태들을 객체로 구현한 것임.
from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDLK_a, get_time
import math


# define event check functions
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


class Sleep:
    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100, math.pi / 2, '', boy.x - 25,
                                          boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100, math.pi / 2, '', boy.x - 25,
                                          boy.y - 25, 100, 100)


class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):  # 우측으로 Run
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e):  # 좌측으로 Run
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class AutoRun:
    @staticmethod
    def enter(boy, e):
        if boy.action == 2:
            boy.dir, boy.action = -1, 0  # 좌측
        elif boy.action == 3:
            boy.dir, boy.action = 1, 1  # 우측

        boy.autorun_start_time = get_time()
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

        # 좌우 이동 벽 충돌 체크
        if boy.x <= 30:
            boy.dir, boy.action = 1, 1
        elif boy.x >= 770:
            boy.dir, boy.action = -1, 0

        # boy 위치 이동
        boy.x += boy.dir * 30

        if get_time() - boy.autorun_start_time > 5:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        pass


    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 30, 200, 200)


class Idle:
    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.idle_start_time = get_time()
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.idle_start_time > 3:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        print('IDLE Do')
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class StateMachine:
    def __init__(self, boy):
        self.cur_state = Idle
        self.boy = boy
        self.transitions = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, a_down: AutoRun},
            Run: {right_down: Idle, left_down: Idle, left_up: Idle, right_up: Idle},
            Sleep: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, space_down: Idle},
            AutoRun: {time_out: Idle, right_down: Run, left_down: Run}
        }

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True
        return False

    def start(self):
        self.cur_state.enter(self.boy, ('NONE', 0))

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()
