# This file is used to test the functionality of the toolkit
# Can be ignored

topics = ["/battery_state", "/cliff_intensity", "/cmd_audio", "/cmd_lightring", "/cmd_vel", "/hazard_detection",
          "/imu", "/interface_buttons", "/ir_intensity", "/ir_opcode", "/kidnap_status",
          "/mobility_monitor/transition_event", "/mouse", "/odom", "/parameter_events",
          "/robot_state/transition_event", '/rosout', "/slip_status", "/static_transform/transition_event",
          "/stop_status", "/tf", "/tf_static", "/wheel_status", "/wheel_ticks", "/wheel_vels"]

actions = ["/audio_note_sequence [irobot_create_msgs/action/AudioNoteSequence]",
           "/dock [irobot_create_msgs/action/Dock]",
           "/drive_arc [irobot_create_msgs/action/DriveArc]",
           "/drive_distance [irobot_create_msgs/action/DriveDistance]",
           "/led_animation [irobot_create_msgs/action/LedAnimation]",
           "/navigate_to_position [irobot_create_msgs/action/NavigateToPosition]",
           "/rotate_angle [irobot_create_msgs/action/RotateAngle]",
           "/undock [irobot_create_msgs/action/Undock]",
           "/wall_follow [irobot_create_msgs/action/WallFollow]"]
