
import os
import struct
import numpy as np
import zlib
import imageio
import PIL

COMPRESSION_TYPE_COLOR = {-1: 'unknown', 0: 'raw', 1: 'png', 2: 'jpeg'}
COMPRESSION_TYPE_DEPTH = {-1: 'unknown', 0: 'raw_ushort', 1: 'zlib_ushort', 2: 'occi_ushort'}


class RGBDFrame():
    def load(self, file_handle):
        self.camera_to_world = np.asarray(struct.unpack('f'*16, file_handle.read(16*4)),
                                          dtype=np.float32).reshape(4, 4)
        self.timestamp_color = struct.unpack('Q', file_handle.read(8))[0]
        self.timestamp_depth = struct.unpack('Q', file_handle.read(8))[0]
        self.color_size_bytes = struct.unpack('Q', file_handle.read(8))[0]
        self.depth_size_bytes = struct.unpack('Q', file_handle.read(8))[0]
        self.color_data = ''.join(struct.unpack(
            'c'*self.color_size_bytes, file_handle.read(self.color_size_bytes)))
        self.depth_data = ''.join(struct.unpack(
            'c'*self.depth_size_bytes, file_handle.read(self.depth_size_bytes)))

    def decompress_depth(self, compression_type):
        if compression_type == 'zlib_ushort':
            return self.decompress_depth_zlib()
        else:
            raise

    def decompress_depth_zlib(self):
        return zlib.decompress(self.depth_data)

    def decompress_color(self, compression_type):
        if compression_type == 'jpeg':
            return self.decompress_color_jpeg()
        else:
            raise

    def decompress_color_jpeg(self):
        return imageio.imread(self.color_data)


class SensorData:
    def __init__(self, filename):
        self.version = 4
        self.load(filename)

    def load(self, filename):
        with open(filename, 'rb') as f:
            version = struct.unpack('I', f.read(4))[0]
            assert self.version == version
            strlen = struct.unpack('Q', f.read(8))[0]
            self.sensor_name = ''.join(struct.unpack('c'*strlen, f.read(strlen)))
            self.intrinsic_color = np.asarray(struct.unpack('f'*16, f.read(16*4)),
                                              dtype=np.float32).reshape(4, 4)
            self.extrinsic_color = np.asarray(struct.unpack('f'*16, f.read(16*4)),
                                              dtype=np.float32).reshape(4, 4)
            self.intrinsic_depth = np.asarray(struct.unpack('f'*16, f.read(16*4)),
                                              dtype=np.float32).reshape(4, 4)
            self.extrinsic_depth = np.asarray(struct.unpack('f'*16, f.read(16*4)),
                                              dtype=np.float32).reshape(4, 4)
            self.color_compression_type = COMPRESSION_TYPE_COLOR[struct.unpack('i', f.read(4))[0]]
            self.depth_compression_type = COMPRESSION_TYPE_DEPTH[struct.unpack('i', f.read(4))[0]]
            self.color_width = struct.unpack('I', f.read(4))[0]
            self.color_height = struct.unpack('I', f.read(4))[0]
            self.depth_width = struct.unpack('I', f.read(4))[0]
            self.depth_height = struct.unpack('I', f.read(4))[0]
            self.depth_shift = struct.unpack('f', f.read(4))[0]
            num_frames = struct.unpack('Q', f.read(8))[0]
            self.frames = []
            for i in range(num_frames):
                frame = RGBDFrame()
                frame.load(f)
                self.frames.append(frame)

    def export_depth_images(self, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print 'exporting', len(self.frames), ' depth frames to', output_path
        for f in range(len(self.frames)):
            depth_data = self.frames[f].decompress_depth(self.depth_compression_type)
            depth = np.fromstring(depth_data, dtype=np.uint16).reshape(self.depth_height,
                                                                       self.depth_width)
            imageio.imwrite(os.path.join(output_path, str(f) + '.png'), depth)

    def export_color_images(self, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print 'exporting', len(self.frames), 'color frames to', output_path
        for f in range(len(self.frames)):
            color = self.frames[f].decompress_color(self.color_compression_type)
            imageio.imwrite(os.path.join(output_path, str(f) + '.jpg'), color)

    def save_mat_to_file(self, matrix, filename):
        with open(filename, 'w') as f:
            for line in matrix:
                np.savetxt(f, line[np.newaxis], fmt='%f')

    def export_poses(self, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print 'exporting', len(self.frames), 'camera poses to', output_path
        for f in range(len(self.frames)):
            self.save_mat_to_file(self.frames[f].camera_to_world,
                                  os.path.join(output_path, str(f) + '.txt'))

    def export_intrinsics(self, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print 'exporting camera intrinsics to', output_path
        self.save_mat_to_file(self.intrinsic_color, os.path.join(output_path,
                                                                 'intrinsic_color.txt'))
        self.save_mat_to_file(self.extrinsic_color, os.path.join(output_path,
                                                                 'extrinsic_color.txt'))
        self.save_mat_to_file(self.intrinsic_depth, os.path.join(output_path,
                                                                 'intrinsic_depth.txt'))
        self.save_mat_to_file(self.extrinsic_depth, os.path.join(output_path,
                                                                 'extrinsic_depth.txt'))

    def export_depth_images_rob(self, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print 'exporting', len(self.frames), ' depth frames to', output_path
        for f in range(len(self.frames)):
            depth_data = self.frames[f].decompress_depth(self.depth_compression_type)
            depth = np.fromstring(depth_data, dtype=np.uint16).reshape(self.depth_height,
                                                                       self.depth_width)
            depth = (depth.astype(np.float32) / 1000.0 * 256.0).astype(np.uint16)
            imageio.imwrite(os.path.join(output_path, str(f).zfill(10) + '.png'), depth)

    def export_color_images_rob(self, output_path, full_resolution):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print 'exporting', len(self.frames), 'color frames to', output_path
        for f in range(len(self.frames)):
            color = self.frames[f].decompress_color(self.color_compression_type)
            if full_resolution:
                color = PIL.Image.fromarray(color)
            else:
                color = PIL.Image.fromarray(color).resize([self.depth_width, self.depth_height])
            color.save(os.path.join(output_path, str(f).zfill(10) + '.png'))

    def save_intrinsic_to_file_rob(self, matrix, filename):
        with open(filename, 'w') as f:
            np.savetxt(f, matrix[:3, :3], fmt='%f', newline=' ')

    def export_intrinsics_rob(self, output_path, full_resolution):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print 'exporting camera intrinsics to', output_path
        if not full_resolution:
            self.intrinsic_color[0, 0] *= float(self.depth_width) / float(self.color_width)
            self.intrinsic_color[0, 2] *= float(self.depth_width - 1) / float(self.color_width - 1)
            self.intrinsic_color[1, 1] *= float(self.depth_height) / float(self.color_height)
            self.intrinsic_color[1, 2] *= float(self.depth_height - 1) / float(self.color_height - 1)
        for f in range(len(self.frames)):
            self.save_intrinsic_to_file_rob(self.intrinsic_color,
                                            os.path.join(output_path, str(f).zfill(10) + '.txt'))
