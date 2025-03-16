# Fingerprint Recognition System

## Contributors to this work:
[Ashish Rodi](https://www.linkedin.com/in/ashish-rodi-a7328a269/), [Samarth Arole](https://www.linkedin.com/in/samarth-arole-704748262/), [Aryan Mundra](https://www.linkedin.com/in/aryan-mundra-512b64218/)

## Abstract
This project presents a fingerprint recognition system using an ESP32 microcontroller, an R307 fingerprint sensor, and a local server for data storage and verification. The system is designed for biometric authentication and enrollment, providing secure and efficient fingerprint data handling. It leverages TCP communication over Wi-Fi, enabling real-time data exchange between the ESP32 and a remote server. The project allows for switching between two operational modes: enrolling new fingerprints and verifying existing fingerprints. This report outlines the design, implementation, and functionality of the system, focusing on hardware-software integration and TCP-based data transfer.

**Keywords**: Fingerprint recognition, ESP32, R307 sensor, TCP communication, Wi-Fi, biometric authentication, image processing, SIFT algorithm, FLANN matcher, enrollment, verification.

## Introduction
Biometric systems, such as fingerprint recognition, are widely used for secure identification and access control due to their reliability and ease of use. This project focuses on developing a fingerprint recognition system using an ESP32 microcontroller and an R307 fingerprint sensor, which connects to a local server for storing and verifying fingerprint data.

While the R307 fingerprint sensor can store up to 128 fingerprints internally, relying on sensor-based storage introduces scalability limitations. If fingerprints are stored directly on each sensor, every fingerprint would need to be registered on every individual sensor, leading to time-consuming and inconsistent registration processes. To overcome this, the project uses a local server to store all fingerprint data in a centralized database.

Using a centralized server improves efficiency, enhances security, and simplifies management, making it easier to protect, back up, and manage access control for all connected devices. This setup ensures scalability and seamless integration of new sensors without requiring manual configuration.

The system operates in two distinct modes:
1. **Enrollment Mode**: Captures fingerprint images in multiple parts, stores them on the server, and creates a fingerprint database.
2. **Verification Mode**: Uses SIFT and FLANN-based matcher to compare captured fingerprints with stored ones, ensuring accurate fingerprint recognition.

## Literature Survey
Several papers were referenced to understand fingerprint recognition:
- Ganesh et al. implemented a basic fingerprint lock system using Arduino and a solenoid lock.
- Ramakrishna et al. developed a biometric lock using ESP32, a fingerprint sensor, and an ESP32 camera for verification.
- Maheshwar and Asish explored different feature extraction methods like HOG, Harris Corner detector, and ORB descriptor.
- Juby and Gladstone used FLANN matcher for leaf identification, showcasing its effectiveness in pattern matching.
- The FPM library was identified as a crucial tool for extracting fingerprint images from the sensor buffer.

Unlike previous works, this project implements server-based fingerprint verification using SIFT and the FLANN matcher.

## Methodology
### 1. Hardware and Sensor Integration
- **ESP32**: A microcontroller with Wi-Fi capabilities, communicating with the R307 fingerprint sensor via UART.
- **R307 Fingerprint Sensor**: Captures grayscale fingerprint images, transmitting raw data to the ESP32.
- **Wi-Fi and TCP Communication**: The ESP32 establishes a TCP connection to transmit fingerprint data to the server.

### 2. Server and Data Handling
- **Enrollment Mode**: Captures fingerprint images in multiple parts and stores them in a structured directory on the server.
- **Verification Mode**: Compares real-time fingerprint scans with stored images using SIFT for feature detection and the FLANN matcher for matching.
- **Data Transfer**: Uses TCP to reliably transmit fingerprint images in small packets, reconstructing them on the server.

### 3. Image Processing and Fingerprint Matching
- **SIFT (Scale-Invariant Feature Transform)**: Extracts keypoints and descriptors from fingerprint images.
- **FLANN-based Matcher**: Efficiently compares extracted keypoints for accurate fingerprint matching.
- **Mode Switching**: Users toggle between enrollment and verification modes using a Flask-based web interface.

### 4. Key Components
- **ESP32 and Wi-Fi**: Enables wireless biometric authentication.
- **FPM Library**: Extracts raw fingerprint image data from the sensor.
- **TCP Communication**: Ensures reliable image data transmission.
- **Flask Web Interface**: Simplifies user interaction and mode switching.

## Results and Discussion
- **Fingerprint images were successfully captured and stored** using the FPM library and transferred to the server.
- **Verification process achieved high accuracy** using SIFT and FLANN-based matcher.
- **Performance Comparison**:
  - FLANN-based matcher provided higher accuracy compared to ORB.
  - ORB was faster but produced more false positives.
 
    ![circuit connection](https://github.com/user-attachments/assets/fd4ab399-01a2-4779-b08b-efe062c59647)
![fingerprint variations](https://github.com/user-attachments/assets/e490bc41-dd03-4c7a-9de8-ca033a32bc86)


Testing results demonstrated consistent fingerprint matching with a best match score greater than 1, setting a verification threshold to minimize false positives.

## Conclusion
This project successfully implements a fingerprint recognition system using ESP32, R307 sensor, and a server-based verification approach. The use of TCP communication, SIFT feature extraction, and FLANN matcher ensures accurate and scalable biometric authentication. The system provides a robust, wireless, and centralized fingerprint management solution suitable for secure access control applications.

## Future Work
- Enhancing security with encrypted data transmission.
- Implementing additional biometric features like facial recognition.
- Optimizing image processing for faster verification.

## References
[1] Ganesh et al., "Fingerprint-based lock system using Arduino."
[2] Ramakrishna et al., "ESP32-based biometric access control."
[3] Maheshwar & Asish, "Feature extraction methods for fingerprint matching."
[4] Juby & Gladstone, "Leaf identification using FLANN matcher."
[5] FPM Library Documentation.



