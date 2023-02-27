import time
import cv2 
import mediapipe-silicon as mp
import threading

# For webcam input:
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


#--------------------------------FUNCIONES------------------------------------#

def countdown(t): # define the countdown func.
    while t:
        timer = t
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

def grabacionGesto(results_hands):
    global grabar
    if grabar: 
        #No se guarda el vídeo - sacamos datos
        # BUCLE #
        #Se graba 2 segundos solo y se extraen los puntos
        #Draw the hand annotations on the image.

        for hand_landmarks in results_hands.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
            
        cv2.imshow('MediaPipe Hands', cv2.flip(frame, 1))     
        #No se guarda el vídeo - sacamos datos
        #countdown(3) NO PUEDE FRENAR EL PROGRAMA TIENE QUE SER ATRÁS
        #Se graba 1 segundo solo y se extraen los puntos
        
        #Se crea una lista de frames en la que recopilaremos los puntos del mediapipe durante eses 2 segundos
        global hand_coords
        for id, lm in enumerate(hand_landmarks.landmark):
            hand_coords.append((lm.x, lm.y, lm.z))

        # #Si no encuentra mano en el frame rellena con ceros:      
        # else:
        #     hand_coords = []
        #     for i in range(21):
        #         hand_coords.append((0,0,0))
                 
def waitForThis():
    #print("Acabaron los 2 segundos")
    global acaboTimer 
    acaboTimer = True
    
#--------------------------------FUNCIONES------------------------------------#
def funcion():
    #Si no se detecta mano, graba será False
    grabar = False
    acaboTimer = False #Se usa para capar el vídeo cuando sean los 2 segundos
    hand_coords = [] #Tiene landmarks de la mano
    mark=1 #flag pa detectar mano. Si vale 1 se habilitan 3 segundos antes de mediapipe
    countdown=3
    cont=0
    num_frames=60
    prim_fase=True
    print_atras=True
    text=""

    #Definimos la captura
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Definir el rectángulo deseado en el centro de la imagen
    rect_width = 200
    rect_height = 200
    rect_x = int((width - rect_width) // 2)
    rect_y = int((height - rect_height) // 2)
    print(rect_x)
    print(rect_y)


    with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

        while cap.isOpened():

            ret, frame = cap.read()
            if ret:
                # Procesar el cuadro con Mediapipe para obtener las coordenadas
                frame_cambiado = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results_hands = hands.process(frame_cambiado)
                cv2.imshow('MediaPipe Hands', frame)

                #Si encuentra mano EN EL RECTÁNGULO se habilita cuenta atrás:
                if results_hands.multi_hand_landmarks and mark==1:
                    prim_fase=True
                    for hand_landmarks in results_hands.multi_hand_landmarks:
                        hand_coords = []

                        for id, lm in enumerate(hand_landmarks.landmark):
                            hand_coords.append((lm.x, lm.y, lm.z))

                        x=hand_coords[0][0] * frame.shape[1] #Para que non estea normalizado
                        y=hand_coords[0][1] * frame.shape[0]
                        #mp_drawing.draw_landmarks(frame,hand_landmarks,mp_hands.HAND_CONNECTIONS,mp_drawing_styles.get_default_hand_landmarks_style(),mp_drawing_styles.get_default_hand_connections_style())

                        # Comprobar si la muñeca está dentro del rectángulo
                        if (rect_x < x < rect_x+rect_width) and (rect_y < y < rect_y+rect_height):
                            # Mostrar un mensaje en la pantalla # Mostrar el fotograma y el rectángulo
                            #cv2.imshow("Video", frame)
                            print("Comenzaremos a capturar el gesto en: ")
                            for i in range(3, 0, -1):
                                mark=0
                                print_atras=True
                                text=str(i)
                                # cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                print(text)
                                time.sleep(1)


                            print("Capturando gesto a continuación!")

                start_time = time.monotonic()

                if mark == 0 and cont<=num_frames:
                    prim_fase=False
                    print_atras=False
                    if results_hands.multi_hand_landmarks:
                        for hand_landmarks in results_hands.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())

                    #facer ecuacion conta atrás cos 60 frames
                    if cont == 0:
                        print("Quedan 2 segundos")
                    if cont == num_frames//2:
                        print("Queda 1 segundo")
                    cont=cont+1

                    # reiniciar mark tras 2 segundos de grabacion a 1
                if cont >= num_frames:
                     print("Ata eiquí, chiño! Procesando gesto...")
                     mark=1
                     cont=0
                     prim_fase=True
                     print_atras=True
                     #PROCESAR ACÁ#####################################################

                #poñer flag pa que só se poña na primeira fase
                if prim_fase==True:
                    # if print_atras==True:
                    #     cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.rectangle(frame, (rect_x, rect_y), (rect_x+rect_width, rect_y+rect_height), (0, 255, 0), 2)

                cv2.imshow('MediaPipe Hands', cv2.flip(frame, 1))

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
            else: print("Error durante la grabación")



        cap.release()
