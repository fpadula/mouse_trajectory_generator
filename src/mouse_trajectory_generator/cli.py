from white_board import WhiteBoard, WhiteBoardPlayer, WhiteBoardRecorder
import cv2
import numpy as np
from scipy import ndimage


def main():
    """Main method
    """

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
        'image':
        {
            'triggers': ['image', 'i'],
            'usage': '[FILE] [ROTATION] \n  Loads an image to the board and apply a rotation to it.'
            ' If FILE is blank, load a sample image.'
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
    loaded_img = None
    while cmd not in command_types['exit']['triggers']:
        cmd = input('>')
        split_cmd = cmd.split()
        if len(split_cmd) > 1:
            cmd_args = split_cmd[1:]
        elif len(split_cmd) == 0:
            continue
        else:
            cmd_args = ''
        cmd_type = split_cmd[0]
        if cmd_type in command_types['play']['triggers']:
            if cmd_args[0] == '':
                path = './data/data_sample.csv'
            else:
                path = cmd_args[0]
            board = WhiteBoard('Data player', drawable=False)
            board.enable()
            if loaded_img is not None:
                board.draw_image(loaded_img, pos=(256, 256), anchor='center')
            player = WhiteBoardPlayer(board)
            player.play(file_path=path)
            board.disable()
        elif cmd_type in command_types['record']['triggers']:
            if cmd_args[0] == '':
                path = './data/data_sample.csv'
            else:
                path = cmd_args[0]
            board = WhiteBoard('Data recorder')
            recorder = WhiteBoardRecorder(board)
            board.enable()
            if loaded_img is not None:
                board.draw_image(loaded_img, pos=(256, 256), anchor='center')
            recorder.record(50, path)
            while board.draw():
                try:
                    pass
                except KeyboardInterrupt:
                    board.disable()
                    return
            recorder.stop()
            board.disable()
        elif cmd_type in command_types['image']['triggers']:
            if cmd_args[0] == '':
                path = './cup.png'
            else:
                path = cmd_args[0]
            rotation = float(cmd_args[1])
            loaded_img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)
            loaded_img = ndimage.rotate(loaded_img, rotation, cval=255)
        elif cmd_type in command_types['help']['triggers']:
            msg = '== Available commands == \n'
            for cmd_name, cmd_fields in command_types.items():
                msg += f'- {cmd_name}{cmd_fields["usage"]}\n'
            print(msg)


if __name__ == '__main__':
    main()
