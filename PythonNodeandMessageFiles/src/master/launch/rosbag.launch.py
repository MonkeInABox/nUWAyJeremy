import launch

def generate_launch_description():
    return launch.Launch.Description([
        launch.actions.ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '--snapshot-mode'],
            output='screen'
        )
    ])
