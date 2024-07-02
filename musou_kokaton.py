import math
import os
import random
import sys
import time
import pygame as pg
#�ύX�_

WIDTH, HEIGHT = 1600, 900  # �Q�[���E�B���h�E�̕��C����
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct:pg.Rect) -> tuple[bool, bool]:
    """
    Rect�̉�ʓ��O����p�̊֐�
    �����F�������Ƃ�Rect�C�܂��́C���eRect�C�܂��̓r�[��Rect
    �߂�l�F���������茋�ʁC�c�������茋�ʁiTrue�F��ʓ��^False�F��ʊO�j
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:  # �������̂͂ݏo������
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:  # �c�����̂͂ݏo������
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    org���猩�āCdst���ǂ��ɂ��邩���v�Z���C�����x�N�g�����^�v���ŕԂ�
    ����1 org�F���eSurface��Rect
    ����2 dst�F�������Ƃ�Surface��Rect
    �߂�l�Forg���猩��dst�̕����x�N�g����\���^�v��
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    �Q�[���L�����N�^�[�i�������Ƃ�j�Ɋւ���N���X
    """
    delta = {  # �����L�[�ƈړ��ʂ̎���
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        �������Ƃ�摜Surface�𐶐�����
        ����1 num�F�������Ƃ�摜�t�@�C�����̔ԍ�
        ����2 xy�F�������Ƃ�摜�̈ʒu���W�^�v��
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # �f�t�H���g�̂������Ƃ�
        self.imgs = {
            (+1, 0): img,  # �E
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # �E��
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # ��
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # ����
            (-1, 0): img0,  # ��
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # ����
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # ��
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # �E��
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        �������Ƃ�摜��؂�ւ��C��ʂɓ]������
        ����1 num�F�������Ƃ�摜�t�@�C�����̔ԍ�
        ����2 screen�F���Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        �����L�[�ɉ����Ă������Ƃ���ړ�������
        ����1 key_lst�F�����L�[�̐^���l���X�g
        ����2 screen�F���Surface
        """
        #speed up
        # if key_lst[pg.K_LSHIFT]:
        #     self.speed = 20
        # else:
        #     self.speed = 10

        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        # if self.state == "hyper":
        #     self.hyper_life -= 1
        #     self.image = pg.transform.laplacian(self.image)
        # if self.hyper_life < 0:
        #     self.state = "normal"
        screen.blit(self.image, self.rect)


class Bomb(pg.sprite.Sprite):
    """
    ���e�Ɋւ���N���X
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        ���e�~Surface�𐶐�����
        ����1 emy�F���e�𓊉�����G�@
        ����2 bird�F�U���Ώۂ̂������Ƃ�
        """
        super().__init__()
        rad = random.randint(10, 50)  # ���e�~�̔��a�F10�ȏ�50�ȉ��̗���
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # ���e�~�̐F�F�N���X�ϐ����烉���_���I��
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # ���e�𓊉�����emy���猩���U���Ώۂ�bird�̕������v�Z
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        ���e�𑬓x�x�N�g��self.vx, self.vy�Ɋ�Â��ړ�������
        ���� screen�F���Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    �r�[���Ɋւ���N���X
    """
    def __init__(self, bird: Bird):
    #def __init__(self, bird: Bird, angle0: float=0):
        """
        �r�[���摜Surface�𐶐�����
        ���� bird�F�r�[������������Ƃ�
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        #angle = math.degrees(math.atan2(-self.vy, self.vx))+angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        # self.state = "normal"
        # self.hyper_life = -1

    def update(self):
        """
        �r�[���𑬓x�x�N�g��self.vx, self.vy�Ɋ�Â��ړ�������
        ���� screen�F���Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class NeoBeam:
    """
    �l�I�r���Ɋւ���N���X
    """
    def __init__(self, bird: Bird, num: int):
        """
        ����1 bird�F�r�[������������Ƃ�
        ����2 num�F��������r�[���̐�
        """
        self.bird = bird
        self.num = num

    def gen_beams(self) -> list[Beam]:
        """
        ���������̃r�[���𐶐�����
        """
        return [Beam(self.bird, angle) for angle in range(-50, +51, int(100/(self.num-1)))]  


class Explosion(pg.sprite.Sprite):
    """
    �����Ɋւ���N���X
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        ���e����������G�t�F�N�g�𐶐�����
        ����1 obj�F��������Bomb�܂��͓G�@�C���X�^���X
        ����2 life�F��������
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        �������Ԃ�1���Z���������o�ߎ���_life�ɉ����Ĕ����摜��؂�ւ��邱�Ƃ�
        �����G�t�F�N�g��\������
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    �G�@�Ɋւ���N���X
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2)  # ��~�ʒu
        self.state = "down"  # �~�����or��~���
        self.interval = random.randint(50, 300)  # ���e�����C���^�[�o��

    def update(self):
        """
        �G�@�𑬓x�x�N�g��self.vy�Ɋ�Â��ړ��i�~���j������
        �����_���Ɍ��߂���~�ʒu_bound�܂ō~��������C_state���~��ԂɕύX����
        ���� screen�F���Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy


# class Gravity(pg.sprite.Sprite):
#     """
#     ��ʑS�̂ɐ��������d�͏�Ɋւ���N���X
#     """
#     def __init__(self, life):
#         """
#         ��ʑS�̂ɏd�͏�𐶐�����
#         ���� life�F��������
#         """  
#         super().__init__()
#         self.image = pg.Surface((WIDTH, HEIGHT))
#         pg.draw.rect(self.image, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
#         self.image.set_alpha(200)
#         self.rect = self.image.get_rect()
#         self.life = life

#     def update(self):
#         """
#         �������Ԃ�1���Z���C�������Ԓ��͏d�͏��L���ɂ���
#         """
#         self.life -= 1
#         if self.life < 0:
#             self.kill()


class Score:
    """
    �ł����Ƃ������e�C�G�@�̐����X�R�A�Ƃ��ĕ\������N���X
    ���e�F1�_
    �G�@�F10�_
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


def main():
    pg.display.set_caption("�^�I�������Ƃ񖳑o")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    score = Score()

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    #gras=pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird))
            # if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and key_lst[pg.K_LSHIFT]:
            #     beams.add(NeoBeam(bird, 5).gen_beams())
            # elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            # if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            #     if score.value > 200:
            #         gras.add(Gravity(400))
            #         score.value -= 200
            # if event.type == pg.KEYDOWN and event.key == pg.K_CAPSLOCK and len(shields) == 0:
            #     if score.value > 50:
            #         shields.add(Shield(bird, 400))
            #         score.value -= 50
            # if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:
            #     if score.value > -1000:
            #         bird.state = "hyper"
            #         bird.hyper_life = 500
            #         score.value -= 100
        screen.blit(bg_img, [0, 0])

        if tmr%200 == 0:  # 200�t���[����1��C�G�@���o��������
            emys.add(Enemy())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # �G�@����~��Ԃɓ�������Cinterval�ɉ����Ĕ��e����
                bombs.add(Bomb(emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # �����G�t�F�N�g
            score.value += 10  # 10�_�A�b�v
            bird.change_img(6, screen)  # �������Ƃ��уG�t�F�N�g

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # �����G�t�F�N�g
            score.value += 1  # 1�_�A�b�v
        
        # for bomb in pg.sprite.groupcollide(bombs, gras, True, False):
        #     exps.add(Explosion(bomb, 50))  # �����G�t�F�N�g
        #     score.value += 1  # 1�_�A�b�v
        # for emy in pg.sprite.groupcollide(emys, gras, True, False):
        #     exps.add(Explosion(emy, 100))  # �����G�t�F�N�g
        #     score.value += 1  # 1�_�A�b�v
        #     bird.change_img(6, screen)  # �������Ƃ��уG�t�F�N�g

        # for bomb in pg.sprite.spritecollide(bird, bombs, True):
        #     if bird.state == "normal":
        #         bird.change_img(8, screen) # �������Ƃ�߂��݃G�t�F�N�g
        #         score.update(screen)
        #         pg.display.update()
        #         time.sleep(2)
        #         return
        #     if bird.state == "hyper":
        #         exps.add(Explosion(bomb, 50))  # �����G�t�F�N�g
        #         score.value += 1  # 1�_�A�b�v

        # gras.update()
        # gras.draw(screen)
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
import math
import os
import random
import sys
import time
import pygame as pg
#�ύX�_

WIDTH, HEIGHT = 1600, 900  # �Q�[���E�B���h�E�̕��C����
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct:pg.Rect) -> tuple[bool, bool]:
    """
    Rect�̉�ʓ��O����p�̊֐�
    �����F�������Ƃ�Rect�C�܂��́C���eRect�C�܂��̓r�[��Rect
    �߂�l�F���������茋�ʁC�c�������茋�ʁiTrue�F��ʓ��^False�F��ʊO�j
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:  # �������̂͂ݏo������
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:  # �c�����̂͂ݏo������
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    org���猩�āCdst���ǂ��ɂ��邩���v�Z���C�����x�N�g�����^�v���ŕԂ�
    ����1 org�F���eSurface��Rect
    ����2 dst�F�������Ƃ�Surface��Rect
    �߂�l�Forg���猩��dst�̕����x�N�g����\���^�v��
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    �Q�[���L�����N�^�[�i�������Ƃ�j�Ɋւ���N���X
    """
    delta = {  # �����L�[�ƈړ��ʂ̎���
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        �������Ƃ�摜Surface�𐶐�����
        ����1 num�F�������Ƃ�摜�t�@�C�����̔ԍ�
        ����2 xy�F�������Ƃ�摜�̈ʒu���W�^�v��
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # �f�t�H���g�̂������Ƃ�
        self.imgs = {
            (+1, 0): img,  # �E
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # �E��
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # ��
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # ����
            (-1, 0): img0,  # ��
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # ����
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # ��
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # �E��
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        �������Ƃ�摜��؂�ւ��C��ʂɓ]������
        ����1 num�F�������Ƃ�摜�t�@�C�����̔ԍ�
        ����2 screen�F���Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        �����L�[�ɉ����Ă������Ƃ���ړ�������
        ����1 key_lst�F�����L�[�̐^���l���X�g
        ����2 screen�F���Surface
        """
        #speed up
        # if key_lst[pg.K_LSHIFT]:
        #     self.speed = 20
        # else:
        #     self.speed = 10

        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        # if self.state == "hyper":
        #     self.hyper_life -= 1
        #     self.image = pg.transform.laplacian(self.image)
        # if self.hyper_life < 0:
        #     self.state = "normal"
        screen.blit(self.image, self.rect)


class Bomb(pg.sprite.Sprite):
    """
    ���e�Ɋւ���N���X
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        ���e�~Surface�𐶐�����
        ����1 emy�F���e�𓊉�����G�@
        ����2 bird�F�U���Ώۂ̂������Ƃ�
        """
        super().__init__()
        rad = random.randint(10, 50)  # ���e�~�̔��a�F10�ȏ�50�ȉ��̗���
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # ���e�~�̐F�F�N���X�ϐ����烉���_���I��
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # ���e�𓊉�����emy���猩���U���Ώۂ�bird�̕������v�Z
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        ���e�𑬓x�x�N�g��self.vx, self.vy�Ɋ�Â��ړ�������
        ���� screen�F���Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    �r�[���Ɋւ���N���X
    """
    def __init__(self, bird: Bird):
        """
        �r�[���摜Surface�𐶐�����
        ���� bird�F�r�[������������Ƃ�
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        # self.state = "normal"
        # self.hyper_life = -1

    def update(self):
        """
        �r�[���𑬓x�x�N�g��self.vx, self.vy�Ɋ�Â��ړ�������
        ���� screen�F���Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Explosion(pg.sprite.Sprite):
    """
    �����Ɋւ���N���X
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        ���e����������G�t�F�N�g�𐶐�����
        ����1 obj�F��������Bomb�܂��͓G�@�C���X�^���X
        ����2 life�F��������
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        �������Ԃ�1���Z���������o�ߎ���_life�ɉ����Ĕ����摜��؂�ւ��邱�Ƃ�
        �����G�t�F�N�g��\������
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    �G�@�Ɋւ���N���X
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2)  # ��~�ʒu
        self.state = "down"  # �~�����or��~���
        self.interval = random.randint(50, 300)  # ���e�����C���^�[�o��

    def update(self):
        """
        �G�@�𑬓x�x�N�g��self.vy�Ɋ�Â��ړ��i�~���j������
        �����_���Ɍ��߂���~�ʒu_bound�܂ō~��������C_state���~��ԂɕύX����
        ���� screen�F���Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy


# class Gravity(pg.sprite.Sprite):
#     """
#     ��ʑS�̂ɐ��������d�͏�Ɋւ���N���X
#     """
#     def __init__(self, life):
#         """
#         ��ʑS�̂ɏd�͏�𐶐�����
#         ���� life�F��������
#         """  
#         super().__init__()
#         self.image = pg.Surface((WIDTH, HEIGHT))
#         pg.draw.rect(self.image, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
#         self.image.set_alpha(200)
#         self.rect = self.image.get_rect()
#         self.life = life

#     def update(self):
#         """
#         �������Ԃ�1���Z���C�������Ԓ��͏d�͏��L���ɂ���
#         """
#         self.life -= 1
#         if self.life < 0:
#             self.kill()


class Score:
    """
    �ł����Ƃ������e�C�G�@�̐����X�R�A�Ƃ��ĕ\������N���X
    ���e�F1�_
    �G�@�F10�_
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


def main():
    pg.display.set_caption("�^�I�������Ƃ񖳑o")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    score = Score()

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    #gras=pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird))
            # if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            #     if score.value > 200:
            #         gras.add(Gravity(400))
            #         score.value -= 200
            # if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:
            #     if score.value > -1000:
            #         bird.state = "hyper"
            #         bird.hyper_life = 500
            #         score.value -= 100
        screen.blit(bg_img, [0, 0])

        if tmr%200 == 0:  # 200�t���[����1��C�G�@���o��������
            emys.add(Enemy())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # �G�@����~��Ԃɓ�������Cinterval�ɉ����Ĕ��e����
                bombs.add(Bomb(emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # �����G�t�F�N�g
            score.value += 10  # 10�_�A�b�v
            bird.change_img(6, screen)  # �������Ƃ��уG�t�F�N�g

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # �����G�t�F�N�g
            score.value += 1  # 1�_�A�b�v
        
        # for bomb in pg.sprite.groupcollide(bombs, gras, True, False):
        #     exps.add(Explosion(bomb, 50))  # �����G�t�F�N�g
        #     score.value += 1  # 1�_�A�b�v
        # for emy in pg.sprite.groupcollide(emys, gras, True, False):
        #     exps.add(Explosion(emy, 100))  # �����G�t�F�N�g
        #     score.value += 1  # 1�_�A�b�v
        #     bird.change_img(6, screen)  # �������Ƃ��уG�t�F�N�g

        # for bomb in pg.sprite.spritecollide(bird, bombs, True):
        #     if bird.state == "normal":
        #         bird.change_img(8, screen) # �������Ƃ�߂��݃G�t�F�N�g
        #         score.update(screen)
        #         pg.display.update()
        #         time.sleep(2)
        #         return
        #     if bird.state == "hyper":
        #         exps.add(Explosion(bomb, 50))  # �����G�t�F�N�g
        #         score.value += 1  # 1�_�A�b�v

        # gras.update()
        # gras.draw(screen)
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
