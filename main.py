import cv2
import pandas as pd
import numpy as np
from time import time_ns, sleep
from threading import Thread
import logging


class DrawingRecorder:

    def __init__(self, window_title: str, output_file_path: str, poll_freq=50):

        self.window_title = window_title
        self.output_file_path = output_file_path
        self.drawing = False
        self.pt1_x = None
        self.pt1_y = None
        self.img = np.ones((512, 512), np.uint8) * 255
        self.data_dict = {
            'x': [],
            'y': [],
            'l_button_down': [],
            'stamp': []
        }
        self.recording = True
        self.poll_period = 1 / poll_freq
        cv2.namedWindow(self.window_title)
        cv2.setMouseCallback(self.window_title, self.line_drawing)
        self.data_poll_thread = Thread(target=self.poll_mouse_event, args=(1,))
        self.data_poll_thread.start()

    def line_drawing(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.pt1_x, self.pt1_y = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.line(self.img, (self.pt1_x, self.pt1_y),
                         (x, y), color=(0, 0, 0), thickness=3)
                self.pt1_x, self.pt1_y = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.img, (self.pt1_x, self.pt1_y), (x, y), color=(0, 0, 0), thickness=3)

    def poll_mouse_event(self, _):
        t = 0
        t0 = time_ns()
        while self.recording:
            if self.pt1_x is not None:
                self.data_dict['x'].append(self.pt1_x)
                self.data_dict['y'].append(self.pt1_y)
                self.data_dict['stamp'].append(time_ns())
                self.data_dict['l_button_down'].append(int(self.drawing))
            t += 1
            delta = t0 + (t * self.poll_period * 1e9) - time_ns()
            if delta > 0:
                sleep(delta * 1e-9)

    def save_data(self):
        df = pd.DataFrame.from_dict(self.data_dict)
        df['stamp'] -= df.loc[0, 'stamp']
        df.to_csv(self.output_file_path, header=True, index=False)

    def show_image(self):

        cv2.imshow(self.window_title, self.img)
        if cv2.waitKey(1) & 0xFF == 27:
            self.recording = False
            self.data_poll_thread.join()
            self.save_data()
            return False
        return True


class DrawingPlayer:

    def __init__(self, window_title: str, input_file_path: str):

        self.window_title = window_title
        self.df = pd.read_csv(input_file_path)
        self.img = np.ones((512, 512), np.uint8) * 255
        self.curr_frame = 0
        cv2.namedWindow(self.window_title)
        self.playing = True
        self.drawing = False
        self.l_button_down = None
        self.prev_l_button_down = 0
        self.x = 0
        self.prev_x = None
        self.y = 0
        self.prev_y = None
        self.pt1_x = None
        self.pt1_y = None
        self.mouse_state_thread = Thread(target=self.set_mouse_event, args=(1,))
        self.mouse_state_thread.start()

    def draw_frame(self):
        if self.l_button_down == None or not self.playing:
            return
        if self.prev_l_button_down is None or (self.l_button_down == 1 and self.prev_l_button_down == 0):
            mouse_event = 'l_button_down'
        elif self.l_button_down == 0 and self.prev_l_button_down == 1:
            mouse_event = 'l_button_up'
        else:
            mouse_event = 'mouse_move'

        if mouse_event == 'l_button_down':
            self.drawing = True
            self.pt1_x, self.pt1_y = self.x, self.y
        elif mouse_event == 'mouse_move':
            if self.drawing:
                cv2.line(self.img, (self.pt1_x, self.pt1_y),
                         (self.x, self.y), color=(0, 0, 0), thickness=3)
                self.pt1_x, self.pt1_y = self.x, self.y
        elif mouse_event == 'l_button_up':
            self.drawing = False
            cv2.line(self.img, (self.pt1_x, self.pt1_y),
                     (self.x, self.y), color=(0, 0, 0), thickness=3)
        logging.info('Mouse event: %s, x: %s, y:%s, ptx:%s, pty:%s',
                     mouse_event, self.x, self.y, self.pt1_x, self.pt1_y)

    def set_mouse_event(self, _):
        index = 0
        curr_stamp = 0
        while self.playing:
            self.prev_x = self.x
            self.prev_y = self.y
            self.prev_l_button_down = self.l_button_down
            self.x = self.df.loc[index, 'x']
            self.y = self.df.loc[index, 'y']
            self.l_button_down = self.df.loc[index, 'l_button_down']
            prev_stamp = curr_stamp
            curr_stamp = self.df.loc[index, 'stamp']
            index += 1
            if index >= len(self.df.index):
                self.playing = False
                break
            else:
                sleep((curr_stamp - prev_stamp) * 1e-9)

    def show_image(self):
        self.draw_frame()
        cv2.imshow(self.window_title, self.img)
        if cv2.waitKey(1) & 0xFF == 27:
            return False
        return True


def main():
    """Main method
    """
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")

    cmd = ''
    command_types = {
        'play':
        {
            'triggers': ['play', 'p'],
            'usage': '[FILE] \n  Plays a trajectory file. If FILE is blank, plays sample data.'
        },
        'record':
        {
            'triggers': ['record', 'r'],
            'usage': '[FILE] \n  Records a trajectory file. If FILE is blank, records sample data.'
        },

        'help':
        {
            'triggers': ['help', 'h'],
            'usage': '\n  Displays a help message'
        },
        'exit': {
            'triggers': ['quit', 'exit', 'q', 'e'],
            'usage': '\n  Exits the program'
        }
    }
    print('Type a command (h for help, q to quit)')
    while cmd not in command_types['exit']['triggers']:
        cmd = input('>')
        split_cmd = cmd.split()
        if len(split_cmd) > 1:
            cmd_args = split_cmd[1]
        elif len(split_cmd) == 0:
            continue
        else:
            cmd_args = ''
        cmd_type = split_cmd[0]
        if cmd_type in command_types['play']['triggers']:
            if cmd_args == '':
                path = './data/data_sample.csv'
            else:
                path = cmd_args
            board = DrawingPlayer('DataRecorder', path)
            while board.show_image():
                pass
            cv2.destroyAllWindows()
        elif cmd_type in command_types['record']['triggers']:
            if cmd_args == '':
                path = './data/data_sample.csv'
            else:
                path = cmd_args
            board = DrawingRecorder('DataRecorder', path)
            while board.show_image():
                pass
            cv2.destroyAllWindows()
        elif cmd_type in command_types['help']['triggers']:
            msg = '== Available commands == \n'
            for cmd_name, cmd_fields in command_types.items():
                msg += f'- {cmd_name}{cmd_fields["usage"]}\n'
            print(msg)


if __name__ == '__main__':
    main()
