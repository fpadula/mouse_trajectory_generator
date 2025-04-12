import cv2
import numpy as np
from time import time_ns, sleep
from threading import Thread
import pandas as pd


class WhiteBoard:

    QUIT = 113
    CLEAR = 99

    def __init__(self, window_title: str, dim: tuple[int, int] = (512, 512), drawable=True):
        self.window_title = window_title
        self.pen_touching = False
        self.enabled = False
        self.stroke_x0 = None
        self.stroke_y0 = None
        self.event_x = None
        self.event_y = None
        self.prev_event_x = None
        self.prev_event_y = None
        self.prev_l_button_down = None
        self.drawable = drawable
        self.dim = dim
        self.canvas: np.ndarray = None
        self.events = {}
        self.mouse_l_button_down = False

    def mouse_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_l_button_down = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.mouse_l_button_down = False
        self.process_event(x, y, self.mouse_l_button_down)

    def enable(self):
        self.clear()
        self.enabled = True
        cv2.namedWindow(self.window_title)
        if self.drawable:
            cv2.setMouseCallback(self.window_title, self.mouse_event)

    def disable(self):
        self.enabled = False
        cv2.destroyAllWindows()

    def clear(self):
        self.canvas = np.ones(self.dim, np.uint8) * 255

    def process_event(self, x: int, y: int, l_button_down: bool):
        self.event_x = x
        self.event_y = y
        started_touching = l_button_down and not self.prev_l_button_down
        finished_touching = not l_button_down
        moved = self.event_x != self.prev_event_x or self.event_y != self.prev_event_y

        if started_touching:
            self.pen_touching = True
            self.stroke_x0, self.stroke_y0 = self.event_x, self.event_y
        elif moved:
            if self.pen_touching:
                cv2.line(self.canvas, (self.stroke_x0, self.stroke_y0),
                         (self.event_x, self.event_y), color=(0, 0, 0), thickness=3)
                self.stroke_x0, self.stroke_y0 = self.event_x, self.event_y
        elif finished_touching:
            self.pen_touching = False

        self.prev_event_x = self.event_x
        self.prev_event_y = self.event_y
        self.prev_l_button_down = l_button_down

    def get_board_state(self):
        return self.event_x, self.event_y, self.pen_touching

    def draw_image(self, img, pos=(0, 0), anchor='top_left'):
        x_off = 0
        y_off = 0
        if anchor == 'center':
            y_off += - int(img.shape[0] / 2)
            x_off += - int(img.shape[1] / 2)
        elif anchor == 'bot_right':
            y_off += - img.shape[0]
            x_off += - img.shape[1]

        canvas_y_start = pos[0] + y_off
        canvas_y_end = pos[0] + y_off + img.shape[0]
        canvas_x_start = pos[1] + x_off
        canvas_x_end = pos[1] + x_off + img.shape[1]

        if canvas_y_start > self.canvas.shape[0] or canvas_y_end < 0 or \
                canvas_x_start > self.canvas.shape[1] or canvas_x_end < 0:
            raise RuntimeError('Drawing outside canvas region')

        img_y_start = 0
        img_y_end = img.shape[0]
        if canvas_y_start < 0:
            img_y_start = -canvas_y_start
            canvas_y_start = 0
        elif canvas_y_end > self.canvas.shape[0]:
            img_y_end = canvas_y_end - self.canvas.shape[0]
            if img.shape[0] % 2:
                img_y_end -= 1
            canvas_y_end = self.canvas.shape[0]

        img_x_start = 0
        img_x_end = img.shape[1]
        if canvas_x_start < 0:
            img_x_start = -canvas_x_start
            canvas_x_start = 0
        elif canvas_x_end > self.canvas.shape[1]:
            img_x_end = canvas_x_end - self.canvas.shape[1]
            if img.shape[1] % 2:
                img_x_end -= 1
            canvas_x_end = self.canvas.shape[1]

        self.canvas[
            canvas_y_start: canvas_y_end,
            canvas_x_start: canvas_x_end,
        ] = img[img_y_start:img_y_end, img_x_start:img_x_end]

    def draw(self):
        cv2.imshow(self.window_title, self.canvas)
        key_press = cv2.waitKey(1)
        if key_press & 0xFF == self.QUIT:
            self.disable()
            return False
        elif key_press & 0xFF == self.CLEAR:
            self.clear()
        return True


class WhiteBoardRecorder:
    def __init__(self, board: WhiteBoard):
        self.recording = False
        self.board = board
        self.events = {
            'x': [],
            'y': [],
            'l_button_down': [],
            'stamp': []
        }
        self.rec_thread: Thread = None
        self.period: float = None
        self.file_out: str = None

    def clear_events(self):
        for event in self.events.values():
            event.clear()

    def record(self, rec_freq: float, file_out: str = None):
        self.recording = True
        self.period = 1.0 / rec_freq
        self.file_out = file_out
        self.clear_events()
        self.rec_thread = Thread(target=self.rec_loop)
        self.rec_thread.start()

    def stop(self) -> pd.DataFrame:
        self.recording = False
        if self.rec_thread and self.rec_thread.is_alive():
            self.rec_thread.join()
        df = pd.DataFrame.from_dict(self.events)
        if len(df) > 0:
            df['stamp'] -= df.loc[0, 'stamp']
            if self.file_out is not None:
                df.to_csv(self.file_out, header=True, index=False)
        return df

    def rec_loop(self):
        t = 0
        t0 = time_ns()
        while self.recording:
            x, y, pen_touching = self.board.get_board_state()
            if x is not None:
                self.events['x'].append(x)
                self.events['y'].append(y)
                self.events['stamp'].append(time_ns())
                self.events['l_button_down'].append(pen_touching)
            t += 1
            delta = t0 + (t * self.period * 1e9) - time_ns()
            if delta > 0:
                sleep(delta * 1e-9)


class WhiteBoardPlayer:
    def __init__(self, board: WhiteBoard):
        self.playing = False
        self.board = board

    def play(self, file_path: str = '', df: pd.DataFrame = None):
        self.playing = True
        if file_path == '' and df is None:
            raise RuntimeError('No filepath or dataframe specified')
        if file_path != '':
            df = pd.read_csv(file_path)
        index = 0
        while self.playing and index < len(df) - 1:
            t0 = time_ns()
            self.board.draw()
            self.board.process_event(*df.loc[index, ['x', 'y', 'l_button_down']])
            t1 = time_ns()
            delta = df.loc[index + 1, 'stamp'] - df.loc[index, 'stamp'] - (t1 - t0)
            if delta > 0:
                sleep(delta * 1e-9)
            index += 1


def main():
    print('This example illustrates the features of the WhiteBoard class')
    print('Try drawing something, press "q" when done')
    board = WhiteBoard('Drawing board')
    recorder = WhiteBoardRecorder(board)
    board.enable()
    recorder.record(50)
    while board.draw():
        try:
            pass
        except KeyboardInterrupt:
            board.disable()
            return
    df = recorder.stop()
    board.disable()

    print("Now the board will be drawn again")
    board = WhiteBoard('Drawing board', drawable=False)
    board.enable()
    player = WhiteBoardPlayer(board)
    player.play(df=df)
    board.disable()
    return


if __name__ == '__main__':
    main()
