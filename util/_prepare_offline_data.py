"""
Transform json data into csv format.
The pHRI project uses the csv files as an input of the offline
training. To get the data yourself, I strongly recommend using the
pHRI_recorder to record participants' behavior, because this
program deals only with the data structure of pHRI_recorder's
output json file.

@author: Yuting Sun
@email: sunyuting798@gmail.com
"""


import glob
import logging
import re
import json


# fixed as in Kinect v2.
#   head dir: face recognition result {'roll,pitch,yaw'}
#   joint  2: neck, joint 3: head
#   joint  4,  5,  6,  7: LEFT  shoulder, elbow, wrist, hand
#   joint  8,  9, 10, 11: RIGHT shoulder, elbow, wrist, hand
#       all joints dimensions: [x, y, z, roll, pitch, yaw]
#   trackingId: int ID
#   voice activity: boolean
upper_body_param = ['trackingId', 'voice activity', 'head dir', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
frequency = 30  # Hz
buffer = 1000  # number of lines to write at a time


# TODO use str.join() instead
def _set_value(people_obj=None):
    values = ''

    if 'trackingId' not in people_obj:
        logging.critical('no tracking ID found!!')
        raise ValueError
    else:
        values += people_obj['trackingId']
        values += ', '
    
    if 'voice activity' not in people_obj:
        values += 'NaN, '
    else:
        values += people_obj['voice activity']
        values += ', '
    
    if 'head dir' not in people_obj:
        values += 'NaN, ' * 3
    else:
        head = [float(dim) for dim in people_obj['head dir'].split(',')]
        values += f'{head[0]}, {head[1]}, {head[2]}, '
    
    for joint in upper_body_param[3:]:
        if joint not in people_obj:
            values += 'NaN, ' * 6
        else:
            for dim in people_obj[joint]:
                values += str(dim)
                values += ', '

    # remove last ', '
    values = values[:-2]
    
    return values


def _read_frame(json_f):
    text_frame = []
    bracket_stack = 0
    for line in json_f:
        line = line.rstrip()
        if len(line):
            continue
        # push
        if line[-1] == '{':
            bracket_stack += 1
        # pop when }
        elif line[-1] == '}':
            bracket_stack -= 1
        # pop when },
        elif len(line) >= 2 and line[-2] == '}':
            bracket_stack -= 1
        text_frame.append(line)
        if bracket_stack == 0:
            yield json.loads('\n'.join(text_frame))


def transform(origin_folder='./data/raw_data', dest_folder='./data/csv_data'):
    """transform
    Transforms all json file into csv file.

    Parameters
    ----------
    origin_folder: str (default='./data/raw_data/')
        path of origin folder for json files

    dest_folder: str (default='./data/csv_data/)
        path of destination folder for csv files

    Returns
    -------
    0: normal exit
    1: no json files found
    2: critical json format error
    3: IO failure
    """
    file_list = glob.glob(origin_folder + '*.json')
    if not file_list:
        logging.warning('no json file found!')
        return 1
    for file in file_list:
        file_name = re.split(r'[\/\\\.]', file)[-2]
        logging.info(f'processing {file_name}.json ...')
        with open(file, 'r') as json_f, open(dest_folder + file_name + '.csv', 'w') as csv_f:
            # write csv head
            header = 'id, trackingId, voice_activity, '\
                     'head_roll, head_yaw, head_pitch, '
            for param in upper_body_param[3:]:
                header = header + param + '_x, '
                header = header + param + '_y, '
                header = header + param + '_z, '
                header = header + param + '_ro, '
                header = header + param + '_pi, '
                header = header + param + '_ya, '
            header += '\n'
            csv_f.write(header)
            
            frame_generator = _read_frame(json_f)
            
            # first frame, only contains start time
            # TODO how to use start time?
            first_frame = frame_generator.__next__()
            if 'start time' not in first_frame:
                logging.warning('no "start time" infomation found.')
                starttime = 0
            starttime = float(first_frame['start time'])

            # fetch values from each frame, write into csv file
            buffered_values = ''
            line_cnt = 0
            for json_obj in frame_generator:
                if not 'people' in json_obj:
                    body_count = 0
                else:
                    body_count = len(json_obj['people'])
                try:
                    if body_count == 2:
                        values = _set_value(json_obj['people'][0])
                        values += _set_value(json_obj['people'][1])
                    elif body_count == 1:
                        values = _set_value(json_obj['people'][0])
                    elif not body_count:
                        values = _set_value()
                    else:
                        # more than 2 people.
                        # usually means the experimenter(me) accidentally
                        # enters the experiment area.
                        # TODO suppress continuous warning.
                        logging.warning('more than 2 people detected.')
                        pass  # TODO 3 people situation
                except ValueError:
                    return 2
                values += '\n'  # TODO insert ID in front. Consider ID
                # write
                buffered_values += values
                line_cnt += 1
                if line_cnt >= buffer:
                    csv_f.write(buffered_values)
                    buffered_values = ''
                    line_cnt = 0


if __name__ == '__main__':
    transform()
