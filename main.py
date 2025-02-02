import cv2
import numpy as np


class DrawingBoard:
    """A class to represent a drawing board where users can draw lines using mouse events.
    """

    def __init__(self):
        """Initializes the drawing application.
        """

        self.drawing = False
        self.pt1_x, self.pt1_y = None, None
        self.img = np.ones((512, 512), np.uint8) * 255
        cv2.namedWindow('test draw')
        cv2.setMouseCallback('test draw', self.line_drawing)

    def line_drawing(self, event, x, y, flags, param):
        """Handles mouse events for drawing lines on an image.

        Args:
            event (int): The type of mouse event (e.g., left button down, mouse move, left button up).
            x (int): The x-coordinate of the mouse event.
            y (int): The y-coordinate of the mouse event.
            flags (int): Any relevant flags passed by OpenCV.
            param (any): Any extra parameters supplied by OpenCV.
        Behavior:
            - On left button down, starts drawing and records the starting point.
            - On mouse move, if drawing, draws a line from the last point to the current point.
            - On left button up, stops drawing and draws a final line to the current point.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.pt1_x, self.pt1_y = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                cv2.line(self.img, (self.pt1_x, self.pt1_y),
                         (x, y), color=(0, 0, 0), thickness=3)
                self.pt1_x, self.pt1_y = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.img, (self.pt1_x, self.pt1_y), (x, y), color=(0, 0, 0), thickness=3)

    def show_image(self):
        """Displays the current image in a window named 'test draw'.

        Returns:
            bool: False if the 'Esc' key is pressed, True otherwise.
        """
        cv2.imshow('test draw', self.img)
        if cv2.waitKey(1) & 0xFF == 27:
            return False
        return True


def main():
    """Main method
    """
    board = DrawingBoard()
    while board.show_image():
        pass
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
