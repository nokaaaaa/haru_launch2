import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare  

#メモ 自己位置推定において最初の位置を(0,0)となるように壁の距離を決めて、自己位置のとり方が変わるところでも前の自己位置から壁の距離を決定してあげる

def generate_launch_description():
    ld = LaunchDescription()

    DeclareLaunchArgument('field_color', default_value='red',
                          description='Color of the field')
    
    ld.add_action(DeclareLaunchArgument('field_color', default_value='red', description='Color of the field'))
    
    

    hransac_config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "config", "hransac_config.yaml"
    )

    pid_config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "config", "pid_config.yaml"
    )

    od_config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "config", "drive.json"
    )

    rogilink_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "config", "rogilink.json"
    )

    # haru_ransac ノード
    hransac_node = Node(
        package="haru_ransac",
        executable="hransac",
        name="hransac",
        output="screen",
        parameters=[hransac_config_path, {'field_color': LaunchConfiguration('field_color')}]
    )
    
    # pid ノード
    pid_node = Node(
        package="haru_pid",
        executable="pid",
        name="pid",
        output="screen",
        parameters=[pid_config_path, {'field_color': LaunchConfiguration('field_color')}]
    )

    sick_scan_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('sick_scan_xd'), '/launch/sick_picoscan.launch.py'
        ]),
        launch_arguments={
            "hostname": "192.168.12.6",
            "udp_receiver_ip":"192.168.12.1",
            "all_segments_min_deg": "-90",
            "all_segments_max_deg": "90",
         }.items()
    )
    
    
   
    # gui ノード
    gui_node = Node(
        package="haru_gui",
        executable="gui",
        name="gui",
        output="screen",
        parameters=[{'field_color': LaunchConfiguration('field_color')}]
    )
    
    #driveノード
    od_node = Node(
        package="haru_od_tes",
        executable="od",
        name="od",
        output="screen",
        parameters=[{"config_file": od_config_path}]
    )
    #射出ノード
    op_node = Node(
        package="op",
        executable="on",
        name="on",
        output="screen"
    )
    #rogilink
    rogilink_node = Node(
    package='rogilink_flex',
    executable='rogilink_flex',
    name='rogilink_flex',
    parameters=[{
                    'config_path': rogilink_path
    }]
    )
    #マイコンに送るよう
    example_node =Node(
            package='rogilink_flex_example_py',
            executable='example_node',
            name='example_node'
        )


    ld.add_action(hransac_node)
    ld.add_action(pid_node)
    ld.add_action(gui_node)
    ld.add_action(od_node)
    ld.add_action(sick_scan_launch)
    ld.add_action(op_node)
    ld.add_action(rogilink_node)
    ld.add_action(example_node)

    return ld
