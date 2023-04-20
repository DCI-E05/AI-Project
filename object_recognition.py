import cv2
import mediapipe as mp
import tensorflow as tf


mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

model = tf.saved_model.load("./model/efficientdet_d0_coco17_tpu-32/saved_model/")

while True:
    # Отримуємо кадр з камери
    success, img = cap.read()
    
    # Перетворюємо зображення з BGR в RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    img_new = cv2.resize(img_rgb, (512, 512))
    
    input_tensor = tf.convert_to_tensor(img_new)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = model(input_tensor)
    

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
    detections['num_detections'] = num_detections
    
    for i in range(num_detections):
        class_id = int(detections['detection_classes'][i])
        score = detections['detection_scores'][i]
        bbox = detections['detection_boxes'][i]
        if score > 0.5:
            print(class_id)
    # img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # Відображаємо зображення
    cv2.imshow('Video', img)
    
    # Зупиняємо цикл, якщо користувач натиснув клавішу "q"
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
# Звільняємо ресурси
cap.release()
cv2.destroyAllWindows()
