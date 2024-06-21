"""
Created on Fri May 03 08:23:17 2021
Aragon Photonics Labs. S.L.U.

%%% This document is a strictly confidential communication to and solely %%
%%% for the use of the individual or entity recipient and may not be     %%
%%% reproduced or circulated without Aragon Photonics Labs S.L.U. prior  %%
%%% written consent. If you are not the intended recipient, you may not  %%
%%% disclose or use the information in this documentation in any way.    %%

"""

import numpy as np
import matplotlib.pyplot as plt
#import h5py


def Load_2D_Data_bin(fullPath: str) -> list:
    """

    :parameter fullPath: path of bin file

    :return:
    """
    fileID = open(fullPath, "rb")
    fileID.seek(0)
    dataType = np.float64
    "np.dtype('<f8')"

    # Get the FileHeader; The first Position is the FileHeader Size
    headersize = np.fromfile(fileID, dtype=dataType, count=1)
    fHeaderSize = int(headersize[0])
    header_data = np.fromfile(fileID, dtype=dataType, count=(fHeaderSize-1))
    header = np.hstack((headersize, header_data))

    raw_file = np.fromfile(fileID, dtype=dataType)
    fileID.close()

    "-- Get datastructure variables from the FileHeader"
    "Number of points monitored along the fiber"
    mK_to_Strain = 10

    " File type is HDAS_2Dmap_Strain"
    if header[101] == 2:
        N_processed_Points =  int(header[14] - header[12])

    "Build 2D Data Matrix"
    N_Time_Samples = int(len(raw_file) / N_processed_Points)
    
    
    
    try:
        TracesMatrix = raw_file.reshape((N_Time_Samples, N_processed_Points))
        TracesMatrix = TracesMatrix.transpose()
    
    except ValueError:
        TracesMatrix = None
    del raw_file
    TracesMatrix = TracesMatrix * mK_to_Strain

    return [TracesMatrix, header]


def load_h5file(fullPath: str) -> list:
    f2 = h5py.File(fullPath, "r")
    data = f2['data'][:]
    header = f2['header'][:]
    f2.close()
    return data, header



if __name__ == '__main__':
    #directory = r'C:\Users\preciado\OneDrive - Fibercom, S.L\Documentos\componentesSensado\HDAS\Scrips_python\bin2h5\2021_10_22_13h54m40s_HDAS_2Dmap_Strain.hdf5'
    directory = r'D:\TFG25\2021_11_25_07h53m30s_HDAS_2Dmap_Strain.bin'
    [Data_2D, header] = Load_2D_Data_bin(directory) # para cargar desde un archivo .bin
    
   # [Data_2D, header] = load_h5file(directory) # para cargar desde un archivo .hdf5

    # @@@@@@@@@@@@@@@@@@@@@@@@@ CONFIGURACION DE LA MEDIDA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    Spatial_Sampling_Meters = header[1]
    Fiber_Length_Monitored_Meters = header[3]
    N_processed_Points = Data_2D.shape[0]
    N_Time_Samples = Data_2D.shape[1]

    Fiber_Position_Offset = header[11]
    Trigger_Frequency = header[6] / header[15] / header[98]

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    index_distance = 100
    index_time = 1000

    x_distancia = np.arange(0, N_processed_Points) * Spatial_Sampling_Meters + Fiber_Position_Offset
    t_temporal = np.arange(0, N_Time_Samples) / Trigger_Frequency
    
    # Análisis Frecuencia
    
    espectro = np.fft.fft(Data_2D[index_distance, :])     # Calculamos Transformada de Fourier y su espectro
    freq = np.fft.fftfreq(len(espectro), d=1/Trigger_Frequency)  

    # Filtramos frecuencias negativas
    freq_positiva = freq > 0
    freq = freq[freq_positiva]
    espectro = np.abs(espectro[freq_positiva])

    
    
    
    # Plotear

    plt.figure()
    plt.plot(t_temporal, Data_2D[index_distance, :])
    plt.title('Strain at meter {}'.format(int(index_distance * Spatial_Sampling_Meters)))
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (n$\epsilon$)')
    plt.grid()

    plt.figure()
    plt.plot(x_distancia, Data_2D[:, index_time])
    plt.title('Strain over distances at second {}'.format(int(index_time/Trigger_Frequency)))
    plt.ylabel('Strain (n$\epsilon$)')
    plt.xlabel('Distance (m)')
    plt.grid()

    plt.figure()
    plt.imshow(Data_2D.transpose(), vmin=-20, vmax=20, aspect='auto')
    plt.title('2DMap Strain (n$\epsilon$)')
    plt.xlabel('Distance (m)')
    plt.ylabel('Time (s)')
    plt.colorbar()
    
    plt.figure()
    plt.plot(freq, espectro)
    plt.title('Frequency Analysis at meter {}'.format(int(index_distance * Spatial_Sampling_Meters)))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.show()


