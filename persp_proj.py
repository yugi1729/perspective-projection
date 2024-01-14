import pygame
import numpy as np

class FaceRenderer:
    def __init__(self, vertices_file, indices_file):
        self.vertices_file = vertices_file
        self.indices_file = indices_file
        self.vertices = []
        self.indices = []
        self.load_data()
        self.fov = 90
        self.aspect_ratio = 1
        self.near = 0.1
        self.far = 100

        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.white = (255, 255, 255)

        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.z_val = 0.04

        self.font = pygame.font.Font(None, 36)

    def load_data(self):
        """ load data from file """
        with open(self.vertices_file, 'r') as f:
            for line in f:
                if line.strip():
                    x, y, z = map(float, line.strip().split(','))
                    self.vertices.append((x, y, z))

        with open(self.indices_file, 'r') as f:
            for line in f:
                if line.strip():
                    index1, index2, index3 = map(int, line.strip().split(','))
                    self.indices.append((index1, index2, index3))

    def perspective_projection_matrix(self):
        """
        This function calculates a perspective projection matrix based on the field of view (fov),
        aspect ratio (aspect_ratio), near and far clipping planes (near, far).
        Returns:
            - Projection matrix for transforming 3D coordinates to 2D.
        """
        f = 1 / np.tan(np.radians(self.fov / 2))
        return np.array([
            [f / self.aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (self.far + self.near) / (self.near - self.far), (2 * self.far * self.near) / (self.near - self.far)],
            [0, 0, -1, 0]
        ])

    def translate_matrix(self, tx, ty, tz):
        """
        tx (float): Translation along the x-axis.
        ty (float): Translation along the y-axis.
        tz (float): Translation along the z-axis.
        """
        return np.array([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])

    def rotate_x_matrix(self, theta):
        """
        rotate on x axis 
        Rotation equation for x-axis rotation:
        x' = x
        y' = y * cos(theta) - z * sin(theta)
        z' = y * sin(theta) + z * cos(theta)
        """
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])

    def rotate_y_matrix(self, theta):
        """
        rotate on y axis 
        x' = x * cos(theta) + z * sin(theta)
        y' = y
        z' = -x * sin(theta) + z * cos(theta)
        """
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ])

    def rotate_z_matrix(self, theta):
        """ 
        rotate on z axis 
        Rotation equation for z-axis rotation:
        x' = x * cos(theta) - y * sin(theta)
        y' = x * sin(theta) + y * cos(theta)
        z' = z
        """
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def draw_zoom_value(self):
        """ drawing zoom value on screen lower left """
        zoom_text = self.font.render(f'Zoom: {100.00-self.z_val:.3f}', True, (255, 0, 0))
        self.screen.blit(zoom_text, (10, self.height - 40))

    def run(self, mode):
        """ run rendering loop """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_UP:
                        self.angle_x += 0.1
                    elif event.key == pygame.K_DOWN:
                        self.angle_x -= 0.1
                    elif event.key == pygame.K_LEFT:
                        self.angle_y += 0.1
                    elif event.key == pygame.K_RIGHT:
                        self.angle_y -= 0.1
                    elif event.key == pygame.K_z:
                        self.angle_z += 0.1
                    elif event.key == pygame.K_x:
                        self.angle_z -= 0.1
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        if self.z_val - 0.01 <= 0:
                            self.z_val = 0
                        else:
                            self.z_val -= 0.01
                    elif event.button == 5:  # Scroll down
                        self.z_val += 0.01

            self.screen.fill((0, 0, 0))
            # Here '@' operator is used for efficient matrix multiplication 
            projection_matrix = self.perspective_projection_matrix()
            translation_matrix = self.translate_matrix(0, 0, 10 * self.z_val)
            rotation_matrix = (
                self.rotate_x_matrix(self.angle_x) @
                self.rotate_y_matrix(self.angle_y) @
                self.rotate_z_matrix(self.angle_z)
            )
            # select the mode for displaying the object
            if mode == 'points':
                for vertex in self.vertices:
                    transformed_vertex = projection_matrix @ translation_matrix @ rotation_matrix @ np.array(vertex + (1,))
                    transformed_vertex = transformed_vertex[:3] / transformed_vertex[3]
                    x, y = int(transformed_vertex[0] * self.width / 2 + self.width / 2), int(transformed_vertex[1] * self.height / 2 + self.height / 2)
                    pygame.draw.circle(self.screen, self.white, (x, y), 1)
            elif mode == 'wireframe':
                for index in self.indices:
                    vertex1 = self.vertices[index[0]]
                    vertex2 = self.vertices[index[1]]
                    vertex3 = self.vertices[index[2]]

                    transformed_vertex1 = projection_matrix @ translation_matrix @ rotation_matrix @ np.array(vertex1 + (1,))
                    transformed_vertex1 = transformed_vertex1[:3] / transformed_vertex1[3]
                    x1, y1 = int(transformed_vertex1[0] * self.width / 2 + self.width / 2), int(transformed_vertex1[1] * self.height / 2 + self.height / 2)

                    transformed_vertex2 = projection_matrix @ translation_matrix @ rotation_matrix @ np.array(vertex2 + (1,))
                    transformed_vertex2 = transformed_vertex2[:3] / transformed_vertex2[3]
                    x2, y2 = int(transformed_vertex2[0] * self.width / 2 + self.width / 2), int(transformed_vertex2[1] * self.height / 2 + self.height / 2)

                    transformed_vertex3 = projection_matrix @ translation_matrix @ rotation_matrix @ np.array(vertex3 + (1,))
                    transformed_vertex3 = transformed_vertex3[:3] / transformed_vertex3[3]
                    x3, y3 = int(transformed_vertex3[0] * self.width / 2 + self.width / 2), int(transformed_vertex3[1] * self.height / 2 + self.height / 2)

                    pygame.draw.lines(self.screen, self.white, True, [(x1, y1), (x2, y2), (x3, y3)], 1)
            else:
                print('Incorrect disply mode for object, select : points or wireframe.')

            self.draw_zoom_value()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    vertices_file = 'face-vertices.data'
    indices_file = 'face-index.txt'
    
    renderer = FaceRenderer(vertices_file, indices_file)
    renderer.run('wireframe')
