import cv2


# model: https://github.com/Qengineering/MobileNet_SSD_OpenCV_TensorFlow




def prepare_image(frame, classes, model):
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

    return results
