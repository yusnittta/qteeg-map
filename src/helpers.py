from typing import Tuple, Any, List, Optional                                   #Mengimpor tipe data dari modul typing untuk anotasi tipe

#Notasi Warna
def hex2rgb(rgb: str, alpha: Optional[int] = 255) -> Tuple[int, int, int, int]: #Mendefinisikan fungsi hex2rgb yang mengonversi notasi warna HTML ke notasi RGB
    """                                                 #Docstring
    Convert HTML colour notation to rgb notation.       #Mengonversi notasi warna HTML ke notasi RGB
    Parameters                                          
    -----------
    rgb: str                                            #Parameter 'rgb' adalah string yang merupakan representasi warna HTML
        HTML representation of colour.                  #Representasi warna HTML
    alpha: int, optional                                #Parameter opsional 'alpha' adalah nilai saluran alpha (transparansi)
        Optional alpha channel value.                   #Nilai saluran opsional alpha
    Returns                                             
    -----------
    Tuple[int, int, int, int]                           #Mengembalikan nilai Tuple yang berisi nilai desimal untuk merah, hijau, biru, dan alpha
        Decimal values for red, green, blue and alpha.         
    """                            
    rgb = rgb.lstrip('#')                                                       #Menghapus karakter '#' dari awal string jika ada                      
    return tuple(int(rgb[i:i + 2], 16) for i in (0, 2, 4)) + tuple([alpha])     #Mengonversi substring hex menjadi integer dan menggabungkannya dengan nilai alpha

#Menggabungkan Elemen Unik
def extend_unique(list1: List[Any], list2: List[Any]) -> None:      #Mendefinisikan fungsi extend_unique yang menggabungkan elemen unik dari list2 ke list1
    """                                                             #Docstring
    Extend list with unique values of second lists.                 #Menambahkan elemen unik dari list2 ke list1
    Parameters                                         
    -----------
    list1: List[Any]                                    #Parameter 'list1' adalah list dari nilai dengan tipe apapun
        List of values of any type.                     #List dari nilai dengan tipe apapun
    list2: List[Any]                                    #Parameter 'list2' adalah list dari nilai dengan tipe apapun
        List of values of any type.                     #List dari nilai dengan tipe apapun
    Returns                                             
    -----------
    None                                                #Tidak mengembalikan nilai
    """     
    list1.extend([x for x in list2 if x not in list1])  #Menambahkan elemen dari list2 yang tidak ada di list1 ke list1

#Menghasilkan Elemen Baru
def difference(list1: List[Any], list2: List[Any]) -> List:       #Mendefinisikan fungsi difference yang menghasilkan elemen dari list1 yang tidak ada di list2
    """                                                           #Docstring
    Extend list with unique values of second lists.               #Mengembalikan elemen-elemen dari list1 yang tidak ada di list2
    Parameters                                         
    -----------
    list1: List[Any]                                              #Parameter 'list1' adalah list dari nilai dengan tipe apapun
        List of values of any type.                               #List dari nilai dengan tipe apapun
    list2: List[Any]                                              #Parameter 'list2' adalah list dari nilai dengan tipe apapun
        List of values of any type.                               #List dari nilai dengan tipe apapun
    Returns                                            
    -----------
    List                                                          #Mengembalikan list yang berisi elemen dari list1 yang tidak ada di list2
        The first list without elements from the second list.     #List1 yang tidak ada di list2
    """       
    return [x for x in list1 if x not in list2]                   #Mengembalikan list yang berisi elemen dari list1 yang tidak terdapat di list2