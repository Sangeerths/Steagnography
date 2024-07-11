from flask import Flask, request, send_file, render_template, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

# Create dictionaries for character encoding and decoding
d = {chr(i): i for i in range(255)}
c = {i: chr(i) for i in range(255)}

# Store password and message globally for simplicity (not secure for production use)
password = ""
encrypted_message = ""

@app.route('/')
def index():
    return render_template('index.html')

def check_image_suitability(img, message):
    if img is None or len(img.shape) < 3 or img.shape[2] != 3:
        return False, "Image is not an RGB image."
    
    img_pixels = img.shape[0] * img.shape[1]
    required_pixels = (len(message) + 2) // 3
    
    if img_pixels < required_pixels:
        return False, f"Image is too small. Required pixels: {required_pixels}, Available pixels: {img_pixels}"
    
    return True, "Image is suitable for encoding the message."

@app.route('/encrypt', methods=['POST'])
def encrypt():
    global password, encrypted_message
    image = request.files['image']
    message = request.form['message']
    password = request.form['password']
    encrypted_message = message  # Store the message in a global variable

    # Read the image
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    # Check if the image is suitable
    is_suitable, suitability_message = check_image_suitability(img, message)
    if not is_suitable:
        return suitability_message, 400

    n, m, z = 0, 0, 0

    for i in range(len(message)):
        img[n, m, z] = d[message[i]]
        z = (z + 1) % 3
        if z == 0:
            m += 1
            if m == img.shape[1]:
                m = 0
                n += 1

    encrypted_path = 'Encryptedmsg.png'
    cv2.imwrite(encrypted_path, img)
    return send_file(encrypted_path, as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    global password, encrypted_message
    enc_image = request.files['enc_image']
    pas = request.form['decrypt_password']

    # Check if the password is correct
    if password != pas:
        return "Not valid key", 400

    # Read the encrypted image
    img = cv2.imdecode(np.frombuffer(enc_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    message = ""
    n, m, z = 0, 0, 0

    while True:
        try:
            message += c[img[n, m, z]]
            z = (z + 1) % 3
            if z == 0:
                m += 1
                if m == img.shape[1]:
                    m = 0
                    n += 1
                    if n == img.shape[0]:
                        break
        except KeyError:
            break

    # Print "hii" upon successful decryption
  
    return f"Decrypted message: {message}<br>"

if __name__ == '__main__':
    app.run(debug=True)
