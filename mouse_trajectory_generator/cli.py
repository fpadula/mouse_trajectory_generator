from .white_board import WhiteBoard, WhiteBoardPlayer, WhiteBoardRecorder


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
        'sequence':
        {
            'triggers': ['sequence', 's'],
            'usage': '[PREFIX] [AMOUNT] \n  Set sequence mode. Once recording starts, will perform'
            ' AMOUNT recordings prefixed with PREFIX'
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
            recorder.record(50, path)
            while board.draw():
                try:
                    pass
                except KeyboardInterrupt:
                    board.disable()
                    return
            recorder.stop()
            board.disable()
        elif cmd_type in command_types['help']['triggers']:
            msg = '== Available commands == \n'
            for cmd_name, cmd_fields in command_types.items():
                msg += f'- {cmd_name}{cmd_fields["usage"]}\n'
            print(msg)


if __name__ == '__main__':
    main()
