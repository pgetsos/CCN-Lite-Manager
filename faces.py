from face_object import FaceObject

faces_array = []

for num in range(1, 20):
    newObject = FaceObject()
    newObject.nodenum = num
    newObject.ip = "192.168.1."+str(num)
    faces_array.append(newObject)
