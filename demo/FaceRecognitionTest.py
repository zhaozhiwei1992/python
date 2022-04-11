import face_recognition


class FaceRecognitionTest:

    def isAuthSuccess(self):
        # 获取摄像头中人脸
        # cameraImageRgb = image[:, :, ::-1]
        # 摄像头中的人脸位置, 可能出现多张脸
        cameraImageFaceLocations = []
        # 摄像头中人脸进行编码
        # cameraImageEncodings = face_recognition.face_encodings(image, cameraImageFaceLocations)[0]

        # 使用仓库中文件 测试匹配
        unknownImage = face_recognition.load_image_file("/home/zhaozhiwei/Pictures/authFaces/success/image_0.jpg")
        cameraImageEncodings = face_recognition.face_encodings(unknownImage)[0]

        personNames = []
        knownImageEncodings = []
        # 跟所有保存的人脸比对
        files = ["/home/zhaozhiwei/Pictures/authFaces/success/image_0.jpg"]
        for file in files:
            if file.endswith("jpg") or file.endswith("png"):
                knowImagePath = file
                knownImage = face_recognition.load_image_file(knowImagePath)
                # 将仓库中照片全部编码, 后续比对需要
                knownImageEncodings.append(face_recognition.face_encodings(knownImage)[0])

                biden_encoding = face_recognition.face_encodings(knownImage)[0]
                results = face_recognition.compare_faces([biden_encoding], cameraImageEncodings)
                print("hhh", results)

        results = face_recognition.compare_faces(knownImageEncodings, cameraImageEncodings)
        print("hhaha", results)


if __name__ == '__main__':
    # 相同照片返回True
    known_image = face_recognition.load_image_file("/home/zhaozhiwei/Pictures/authFaces/success/image_0.jpg")
    unknown_image = face_recognition.load_image_file("/home/zhaozhiwei/Pictures/authFaces/success/image_0.jpg")

    biden_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    results = face_recognition.compare_faces([biden_encoding], unknown_encoding)

    print(results)

    # faceRecognitionTest = FaceRecognitionTest()
    # print(faceRecognitionTest.isAuthSuccess())
