from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rviz_2d_overlay_plugins',
            executable='string_to_overlay_text',
            name='string_to_overlay_text_1',
            output='screen',
            parameters=[
                {"string_topic": "errorCodesDisp"},
                {"fg_color": "w"}, # colors can be: r,g,b,w,k,p,y (red,green,blue,white,black,pink,yellow)
                {"bg_color": "bk"},
            ],
        ),
        Node(
            package='rviz_2d_overlay_plugins',
            executable='string_to_overlay_text',
            name='driving_mode',
            output='screen',
            parameters=[
                {"string_topic": "driving_text_mode"},
                {"fg_color": "w"}, # colors can be: r,g,b,w,k,p,y (red,green,blue,white,black,pink,yellow)
                {"bg_color": "bk"},
            ],
        ),
    ])