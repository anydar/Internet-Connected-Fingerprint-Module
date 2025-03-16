import socket
import os
import numpy as np
from PIL import Image
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

# Variable to store the current mode (enroll/verify)
mode = 'enroll'

# Enroll and verify server variables
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 9999       # Port to listen on for fingerprint data (must match ESP32 client)

# Function to handle mode change requests
@app.route('/set_mode', methods=['POST'])
def set_mode():
    global mode
    data = request.get_json()
    if 'mode' in data:
        mode = data['mode']
        print(f"Mode changed to: {mode}")  # Notify mode change
        return f"Mode changed to {mode}", 200
    return "Invalid request", 400

@app.route('/get_mode', methods=['GET'])
def get_mode():
    return jsonify({'mode': mode})

# Function to convert bytes to image
def bytes_to_image(image_data, width=256, height=288):
    img_array = np.zeros((height, width), dtype=np.uint8)
    for i in range(len(image_data)):
        high_pixel = (image_data[i] >> 4) * 17  # Upper 4 bits
        low_pixel = (image_data[i] & 0x0F) * 17  # Lower 4 bits
        row = (i * 2) // width
        col = (i * 2) % width
        img_array[row, col] = high_pixel
        if col + 1 < width:
            img_array[row, col + 1] = low_pixel
    img = Image.fromarray(img_array, mode='L')
    return img

# Enrollment process
def enroll_fingerprints(data, fingerprint_number, part_number):
    expected_image_size = 36736  # For 256x288 4-bit image
    if len(data) >= expected_image_size:
        image = bytes_to_image(data[:expected_image_size])  # Use only the required bytes
        image_filename = f"fingerprint_{fingerprint_number}_{part_number}.bmp"
        image.save(f"./fingerprints/{image_filename}")
        print(f"Saved fingerprint image as {image_filename}")
        return True
    return False

# Fingerprint verification process
def verify_fingerprint(sample_image_data):
    sample_image = bytes_to_image(sample_image_data)

    # Initialize variables for best match
    best_score = 0
    best_file = None

    sift = cv2.SIFT_create()
    kp_sample, des_sample = sift.detectAndCompute(np.array(sample_image), None)

    for file in os.listdir("./fingerprints/"):
        fingerprint_image = cv2.imread(f"./fingerprints/{file}", cv2.IMREAD_GRAYSCALE)
        kp_fp, des_fp = sift.detectAndCompute(fingerprint_image, None)

        # FLANN matcher
        matches = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 10}, {}).knnMatch(des_sample, des_fp, k=2)
        match_points = [p for p, q in matches if p.distance < 0.7 * q.distance]

        # Calculate match score
        keypoints = min(len(kp_sample), len(kp_fp))
        score = len(match_points) / keypoints * 100 if keypoints > 0 else 0

        if score > best_score:
            best_score = score
            best_file = file

    # Verification result
    if best_score > 2.5:
        print(f"Verification successful! Best match: {best_file} with score: {best_score:.2f}")
        return True
    else:
        print(f"Verification failed. Best score: {best_score:.2f}")
        return False

# Function to load the last used fingerprint number from a file
def load_fingerprint_number(file_path='counter.txt'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 1  # Default to 1 if the file is empty or contains invalid data
    return 1  # Default if the file does not exist

# Function to save the current fingerprint number to a file
def save_fingerprint_number(fingerprint_number, file_path='counter.txt'):
    with open(file_path, 'w') as f:
        f.write(str(fingerprint_number))

# Function to handle TCP connections based on the current mode
def handle_fingerprint_data():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Listening for fingerprint data on {HOST}:{PORT}...")

    fingerprint_number = load_fingerprint_number()  # Initialize fingerprint number
    part_counter = 0  # Track part number during enrollment

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            print("Receiving image...")

            data = bytearray()
            while True:
                packet = conn.recv(1024)
                if not packet:
                    break
                data += packet

            if data:
                # Mode-based behavior
                if mode == 'enroll':
                    print("Enrolling fingerprint...")
                    if enroll_fingerprints(data, fingerprint_number, part_counter):
                        print(f"Fingerprint part {part_counter} enrolled successfully.")
                        part_counter += 1
                    if part_counter == 3:
                        print("Enrollment complete. 3 parts saved.")
                        part_counter = 0  # Reset for next enrollment
                        fingerprint_number += 1  # Increment fingerprint number for the next enrollment
                        save_fingerprint_number(fingerprint_number)  # Save the updated fingerprint number

                elif mode == 'verify':
                    print("Starting fingerprint verification...")
                    verification_result = verify_fingerprint(data)

            conn.close()

    except KeyboardInterrupt:
        print("\nShutting down the server.")
    finally:
        server_socket.close()

# Main entry point for Flask app and TCP server
if __name__ == '__main__':
    # Run Flask app in a separate thread for handling mode switching
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False))
    flask_thread.start()

    # Start the fingerprint handling server (this will run in the main thread)
    handle_fingerprint_data()
