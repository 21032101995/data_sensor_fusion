import paho.mqtt.subscribe as subscribe
import numpy as np
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
import json
from scipy.spatial.transform import Rotation as R
import pandas as pd

waypoints = {
     "APPROX_PICK": [0.0000, 0.07430, 0.0000, 3.116, 0.001, -0.039],
     "PICK": [0.000, 0.07430, -0.05520, 3.116, 0.001, -0.039],
     "APPROX_PICK_2": [0.0000, 0.07430, 0.0000, 3.116, 0.001, -0.039],
     "APPROX_PLACE": [0.18280, 0.07430, 0.0000, 3.116, 0.001, -0.039],
     "PLACE": [0.18280, 0.07430, -0.05520, 3.116, 0.001, -0.039],
     "APPROX_PLACE_2": [0.18280, 0.07430, 0.0000, 3.116, 0.001, -0.039],
}

class Build_Dataset():
     def __init__(self):
          self.df = pd.DataFrame()
     def append_data(self, temperature, vibration, pose, label):
          self.df = pd.concat([self.df, pd.DataFrame([{'Temperature': temperature, 'Vibration': vibration, 'X': pose[0], 'Y': pose[1], 'Z': pose[2], 'RX': pose[3], 'RY': pose[4], 'RZ': pose[5], "State": label }])], ignore_index=True)
     def export_csv(self, filename="dataset.csv"):
        self.df.to_csv(filename, index=False, encoding="utf-8")
        print(f"Dataset exportado com sucesso para: {filename}")
class UR_Acquisition():
     def __init__(self):
          self.rtde_c = RTDEControl("192.168.68.114")
          self.rtde_r = RTDEReceive("192.168.68.114")
     def move(self, pose):
          self.rtde_c.moveL(pose, 0.25, 0.5)
     def get_pose(self):
          tcp_pose = self.rtde_r.getActualTCPPose()
          return tcp_pose
          
class MQTT_Subscribe():
    def __init__(self):
        self.broker_ip = "192.168.68.102"
        self.port = 1883
        self.topic = "esp32/sensors"
    def subscribe(self):
       msg = subscribe.simple(self.topic, hostname=self.broker_ip, port=self.port, msg_count=1)
       data = json.loads(msg.payload.decode("utf-8"))
       return data

def pose_trans(p_from, p_from_to):
    pos1 = np.array(p_from[:3])
    rot1 = R.from_rotvec(p_from[3:]).as_matrix()

    T1 = np.eye(4)
    T1[:3, :3] = rot1
    T1[:3, 3] = pos1

    pos2 = np.array(p_from_to[:3])
    rot2 = R.from_rotvec(p_from_to[3:]).as_matrix()

    T2 = np.eye(4)
    T2[:3, :3] = rot2
    T2[:3, 3] = pos2

    T_res = T1 @ T2
    pos_res = T_res[:3, 3]
    rot_res = R.from_matrix(T_res[:3, :3]).as_rotvec()

    return np.concatenate([pos_res, rot_res]).tolist()

def main():
       frame_hugo_phd = [-0.189632, -0.535383, 0.260971, -1.6899e-10, -1.38983e-09, 3.14159]
       mqtt = MQTT_Subscribe()
       UR = UR_Acquisition()
       BD = Build_Dataset()
       i = 0
       while i < 3:
          for key, value in waypoints.items():
               waypoint_base = pose_trans(frame_hugo_phd, waypoints[key])
               UR.move(waypoint_base)
               data = mqtt.subscribe()
               print(data['temperatura'])
               print(data['aceleracao_x'])
               tcp_pose = UR.get_pose()
               print(tcp_pose)
               BD.append_data(data['temperatura'], data['aceleracao_x'], tcp_pose, key)
          i = i + 1
     
       BD.export_csv()

main()