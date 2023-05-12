import cv2


# model: https://github.com/Qengineering/MobileNet_SSD_OpenCV_TensorFlow




def prepare_image(frame, classes, model, draw_results=True):
    blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)
    model.setInput(blob)
    output = model.forward()
    results = []

    for detection in output[0, 0, :, :]:
        confidence = detection[2]
        if confidence > 0.7:
            
            class_id = int(detection[1])
            class_name = classes[class_id]
            results.append(class_name)

            if draw_results:
                x1 = int(detection[3] * frame.shape[1])
                y1 = int(detection[4] * frame.shape[0])
                x2 = int(detection[5] * frame.shape[1])
                y2 = int(detection[6] * frame.shape[0])

                # Відображення результатів на кадрі
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    return frame, results
