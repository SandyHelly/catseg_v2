import cv2
import numpy as np


def get_model():
    """
    load model from onnx
    """
    ONNX_PATH = 'model_inference/dlv3_cats.onnx'
    model = cv2.dnn.readNetFromONNX(ONNX_PATH)
    print('!!!MODEL LOADED!!!')
    return model


def prepocessing():
    """
    load, normalize and transform image to blob
    """
    IMG_PATH = 'app/static/image_storage/users_images/name4pred.jpg'
    image = cv2.imread('{}'.format(IMG_PATH), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.uint8)
    origin_width, origin_height = image.shape[:2]
    mean = np.array([0.485, 0.456, 0.406]) * 255.0
    scale = 1 / 255.0
    std = [0.229, 0.224, 0.225]
    input_blob = cv2.dnn.blobFromImage(image,
                                       scalefactor=scale,
                                       size=(513, 513),
                                       mean=mean,
                                       swapRB=False)
    input_blob[0] /= np.asarray(std, dtype=np.float32).reshape(3, 1, 1)
    return (input_blob, origin_height, origin_width, image)


def postprocessing(model_output, origin_height, origin_width, image):
    """
    overlay image and mask
    """
    out_mask = cv2.resize(np.argmax(model_output[0], axis=0),
                          dsize=(origin_height, origin_width),
                          interpolation=cv2.INTER_NEAREST)
    out_mask[out_mask != 8] = 0
    out_mask[out_mask == 8] = 255
    ch_mask = np.repeat(out_mask[..., np.newaxis], 3, axis=2)
    alpha = 0.5
    saved_img = image * (1 - alpha) + ch_mask * alpha
    return saved_img.astype(np.uint8)


def make_prediction(model):
    """
    run prediction and save result image
    """
    MASK_PATH = 'app/static/image_storage/seg_masks/name4pred_mask.jpg'
    image_pre = prepocessing()
    model.setInput(image_pre[0])
    model_output = model.forward()
    img2save = postprocessing(model_output, image_pre[1], image_pre[2], image_pre[3])
    cv2.imwrite(MASK_PATH, img2save)