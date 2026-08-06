#!/usr/bin/env python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from python_nodes_interfaces.msg import StringMultiArrayStamped

import re
import speech_recognition as sr
import pyaudio
import signal
 
action_list = ["turn", "go", "turn around", "pull over", "pullover", "pull out", "pullin", "stop", "park"]
direction_list = ["left", "right", "straight"]
tertiary_list = ["next", "round about", "intersection", "corner", "first", "second", "third"]
running = True

class speech_node(Node):

    def __init__(self):
        super().__init__("speech_node")

        self.speech_pub = self.create_publisher(StringMultiArrayStamped, "/speech_commands_stamped", 10)
        self.speech_ready_pub = self.create_publisher(String, "/speech_ready", 10)
        
        self.get_logger().info("started speech node")


    

def extract_keywords(string_list, node):
    action_words = '|'.join(action_list)
    regex = r'\b({})\b'
    # python_keywords = set(list)
    # pattern = re.compile(r'\b(' + '|'.join(python_keywords) + r')\b')
    # extracted_keywords = []
#     new_list = []
#     for new_string in string_list:
#         new_list.append(new_string.split('then'))
    word_lists = []
    action_word_list = []
    direction_word_list = []
    tertiary_word_list = []
    
#     for new_string in new_list:
#     print(string_list)
#     for string in string_list:
#         print(string)
    for item in action_list:
    #     print(item)
        if re.search(item, string_list.lower()) != None:
            word = String()
            word.data = item
            action_word_list.append(word)
    for item in direction_list:
        if re.search(item, string_list.lower()) != None:
            word = String()
            word.data = item
            direction_word_list.append(word)
    for item in tertiary_list:
        if re.search(item, string_list.lower()) != None:
            word = String()
            word.data = item
            tertiary_word_list.append((word))
            # extracted_keywords.extend(words)
        #     word_lists.append(word_list)
        #     word_list = []
#     print(type(action_word_list))
#     print(type(direction_word_list[0]))
#     print(type(tertiary_word_list))
         
#     return action_word_list, direction_word_list, tertiary_word_list
    msg = StringMultiArrayStamped()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.action_commands = action_word_list
    msg.direction_commands = direction_word_list
    msg.tertiary_commands = tertiary_word_list
    node.speech_pub.publish(msg)

    return

# def signal_handler(sig, frame):
#     running = False
#     return

def listening_status(node, message):
     msg = String()

     msg.data = message
     node.speech_ready_pub.publish(msg)


def main(args=None):
    rclpy.init()

#     signal.signal(signal.SIGINT, signal_handler)

    node = speech_node()
    rec = sr.Recognizer()
    while running:
        with sr.Microphone() as source:
            listening_status(node, "Now listening.")
        #     rec.adjust_for_ambient_noise(source)
            audio_data = rec.record(source, duration=5)
            text = None
            listening_status(node, "Now processing.")
            start_time = node.get_clock().now()

            try:
                    text_english = rec.recognize_google(audio_data)
                    # text_japanese = rec.recognize_google(audio_data, language="ja-JP")
                    # text_chinese = rec.recognize_google(audio_data, language="ch-CH")
                #     print(text)
                #     node.publish(awl,dwl,twl)
                    
            except:
                    print("No valid text.")
                    pass
            

            if text != None:
                extract_keywords(text_english, node)
            
            end_time = node.get_clock().now()

            duration = end_time - start_time

            node.get_logger.info(duration)


#     rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
