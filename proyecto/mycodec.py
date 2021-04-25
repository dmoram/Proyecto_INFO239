import numpy as np
import cv2
from scipy.signal import medfilt
from scipy import fftpack
from collections import Counter
import heapq


Q = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
              [12, 12, 14, 19, 26, 58, 60, 55],
              [14, 13, 16, 24, 40, 57, 69, 56],
              [14, 17, 22, 29, 51, 87, 80, 62],
              [18, 22, 37, 56, 68, 109, 103, 77],
              [24, 35, 55, 64, 81, 104, 113, 92],
              [49, 64, 78, 87, 103, 121, 120, 101],
              [72, 92, 95, 98, 112, 100, 103, 99]])


def denoise(frame):
    # Eliminacion ruido 1 (Impulsivo)
    
    #Filtro mediana
    #frame1 = medfilt(frame, 5)
    
    # Eliminacion ruido 2 (Periódico)
    #S_img = fftpack.fftshift(fftpack.fft2(frame1))
    #espectro_filtrado = S_img*create_mask(S_img.shape, 0.03)   
    # Reconstrucción
    #framef = np.uint8(fftpack.ifft2(fftpack.ifftshift(espectro_filtrado)))
    
    return frame

def code(frame):
    #
    # Implementa en esta función el bloque transmisor: Transformación + Cuantización + Codificación de fuente
    #
    #framec = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)[:, :, 0]

    calidad = 80 # porcentaje

    #TRANSFORMACION DCT

    DCT2 = lambda g, norm='ortho': fftpack.dct( fftpack.dct(g, axis=0, norm=norm), axis=1, norm=norm)
    IDCT2 = lambda G, norm='ortho': fftpack.idct( fftpack.idct(G, axis=0, norm=norm), axis=1, norm=norm)

    imsize = frame.shape
    dct_matrix = np.zeros(shape=imsize)

    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            dct_matrix[i:(i+8),j:(j+8)] = DCT2(frame[i:(i+8),j:(j+8)])

    #CUANTIZACION

    im_dct = np.zeros(imsize)
    #nnz = np.zeros(dct_matrix.shape)
    if (calidad < 50):
        S = 5000/calidad
    else:
        S = 200 - 2*calidad 
    Q_dyn = np.floor((S*Q + 50) / 100)
    Q_dyn[Q_dyn == 0] = 1
    for i in range(0, imsize[0], 8):
        for j in range(0, imsize[1], 8):
            quant = np.round(dct_matrix[i:(i+8),j:(j+8)]/Q_dyn) 
            im_dct[i:(i+8),j:(j+8)] = IDCT2(quant)
            #nnz[i, j] = np.count_nonzero(quant)

    #CONVERSION ZIG-ZAG
    imz = zigzag(im_dct)
    #RLE
    iml = rle(imz, imz.size)

    #HUFFMANN
    
    imh = huffmann(iml)

    return imh


def decode(message):
    #
    # Reemplaza la linea 24...
    #
    frame = np.frombuffer(bytes(memoryview(message)), dtype='uint8').reshape(480, 848)
    #
    # ...con tu implementación del bloque receptor: decodificador + transformación inversa
    #    
    return frame

def create_mask(dims, frequency, size=10):
    freq_int = int(frequency*dims[0])
    mask = np.ones(shape=(dims[0], dims[1]))
    mask[dims[0]//2-size-freq_int:dims[0]//2+size-freq_int, dims[1]//2-size:dims[1]//2+size] = 0 
    mask[dims[0]//2-size+freq_int:dims[0]//2+size+freq_int, dims[1]//2-size:dims[1]//2+size] = 0
    return mask

def zigzag(frameq):

    i=0
    h = 0,
    v = 0
    vmin = 0
    hmin = 0
    vmax = fr .shape[0]
    hmax = frameq.shape[1]
    output = np.zeros(( vmax * hmax))

    while ((v < vmax) and (h < hmax)):
    	if ((h + v) % 2) == 0:                 # going up
            if (v == vmin):
            	#print(1)
                output[i] = frameq[v, h]        # if we got to the first line
                if (h == hmax):
                    v = v + 1
                else:
                    h = h + 1             
                i = i + 1
            elif ((h == hmax -1 ) and (v < vmax)):   # if we got to the last column
            	#print(2)
            	output[i] = frameq[v, h] 
            	v = v + 1
            	i = i + 1
            elif ((v > vmin) and (h < hmax -1 )):    # all other cases
            	#print(3)
            	output[i] = frameq[v, h] 
            	v = v - 1
            	h = h + 1
            	i = i + 1        
        else:                                    # going down 
        	if ((v == vmax -1) and (h <= hmax -1)):       # if we got to the last line
        		#print(4)
        		output[i] = frameq[v, h] 
        		h = h + 1
        		i = i + 1        
        	elif (h == hmin):                  # if we got to the first column
        		#print(5)
        		output[i] = frameq[v, h] 
        		if (v == vmax -1):
        			h = h + 1
        		else:
        			v = v + 1
        		i = i + 1
        	elif ((v < vmax -1) and (h > hmin)):     # all other cases
        		#print(6)
        		output[i] = frameq[v, h] 
        		v = v + 1
        		h = h - 1
        		i = i + 1
        if ((v == vmax-1) and (h == hmax-1)):          # bottom right element
        	#print(7)        	
        	output[i] = frameq[v, h] 
        	break
    #print ('v:',v,', h:',h,', i:',i)
    return output


def rle(message, n):
    encoded_message = np.zeros(0)
    i = 0

    while (i <= n-1):
        count = 1
        ch = message[i]
        j = i
        while (j < n-1):
            if (message[j] == message[j+1]):
                count = count+1
                j = j+1
            else:
                break
        #encoded_message=encoded_message+str(count)+ch
        encoded_message = np.r_[encoded_message, [count, ch]]
        i = j+1
    return encoded_message
    
def huffmann (tira):
    # Implemetación adaptada de https://rosettacode.org/wiki/Huffman_coding#Python
    
    # Construir dendograma con las probabilidades ordenadas
    dendograma = [[frequencia/len(tira), [simbolo, ""]] for simbolo, frequencia in Counter(tira).items()]
    heapq.heapify(dendograma)
    # Crear el código
    while len(dendograma) > 1:
        lo = heapq.heappop(dendograma)
        hi = heapq.heappop(dendograma)
        for codigo in lo[1:]:
            codigo[1] = '0' + codigo[1]
        for codigo in hi[1:]:
            codigo[1] = '1' + codigo[1]
        heapq.heappush(dendograma, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    # Convertir código a diccionario
    dendograma = sorted(heapq.heappop(dendograma)[1:])
    dendograma = {simbolo : codigo for simbolo, codigo in dendograma} 
    display(dendograma)

    #tira_codificada = ""
    tira_codificada = np.zeros(0)
    for valor in tira:
        #tira_codificada += dendograma[valor]
        tira_codificada = np.r_[tira_codificada, [dendograma[valor]]]

    return tira_codificada

    #display(texto_codificado[:1000])