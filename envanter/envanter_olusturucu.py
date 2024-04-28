import platform
import socket
import os
import psutil
import uuid
import wmi
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

try:
    import GPUtil
except ImportError:
    GPUtil = None

def get_system_info():
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if 'C:' in partition.device:
                if 'ssd' in partition.opts.lower():
                    disk_info = f"SSD: {partition.device} - {psutil.disk_usage(partition.mountpoint).total / (1024 ** 3):.2f} GB"
                    break
                else:
                    disk_info = f"{psutil.disk_usage(partition.mountpoint).total / (1024 ** 3):.2f} GB"
                    break
        else:
            disk_info = 'N/A'
        
        video_card = 'Not implemented'

        system_info = {
            'Operating System': platform.system(),
            'Hostname': socket.gethostname(),
            'Computer Name': os.environ['COMPUTERNAME'],
            'Model': get_system_model(),
            'CPU': get_cpu_model(),
            'RAM': round(psutil.virtual_memory().total / (1024 ** 3), 2),  # Convert to GB
            'Disk': disk_info,
            'Video Card': video_card,
            'Mac address Ethernet': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(2, 7)][::-1]),
            'Mac address Wireless': 'Not implemented',  # Bu bilgiyi almak için ek bir modül veya API kullanmanız gerekebilir
            'Serial Number': get_serial_number(),
            'Chassis': 'Desktop' if platform.machine().lower() == 'x86_64' else 'Notebook'
        }
        return system_info
    except Exception as e:
        print(f"Hata: {e}")
        return None

def get_serial_number():
    try:
        if platform.system() == 'Windows':
            c = wmi.WMI()
            system_serial = c.Win32_BIOS()[0].SerialNumber
        elif platform.system() == 'Linux':
            # Bu, Linux sistemlerinde genellikle çalışır, ancak her zaman doğru sonuç vermez
            with open('/sys/class/dmi/id/product_serial', 'r') as f:
                system_serial = f.read().strip()
        else:
            system_serial = 'Not implemented'
        
        return system_serial
    except Exception as e:
        print(f"Hata: {e}")
        return 'Not implemented'

def get_system_model():
    try:
        if platform.system() == 'Windows':
            c = wmi.WMI()
            system_model = c.Win32_ComputerSystem()[0].Model
        else:
            system_model = platform.machine()
        
        return system_model
    except Exception as e:
        print(f"Hata: {e}")
        return 'Not implemented'

def get_cpu_model():
    try:
        if platform.system() == 'Windows':
            c = wmi.WMI()
            cpu_model = c.Win32_Processor()[0].Name
        else:
            cpu_model = platform.processor()
        
        return cpu_model
    except Exception as e:
        print(f"Hata: {e}")
        return 'Not implemented'

def create_inventory_form(system_info):
    try:
        # Kullanıcıdan bilgileri al
        seri_no = system_info['Serial Number']
        aksesuarlar = input("Bilgisayar Aksesuarları (virgülle ayırarak girin): ").split(",")
        teslim_eden = input("Teslim Eden: ")
        teslim_alan = input("Teslim Alan: ")

        # Kullanıcının ev dizini yolu
        ev_dizini = os.path.expanduser('~')
        # Masaüstü yolu
        masaustu_yolu = os.path.join(ev_dizini, 'Desktop')

        # PDF dosyasının yolunu oluştur
        pdf_adi = input("PDF Dosyasının Adı (uzantı olmadan): ")
        pdf_yolu = os.path.join(masaustu_yolu, f"Zimmet Tutanağı_{teslim_alan}.pdf")

        # PDF dosyasını oluştur
        c = canvas.Canvas(pdf_yolu, pagesize=letter)

        # Başlık ekle
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(300, 750, 'ZIMMET FORMU')

        # Tarih bilgisi ekle (Sağ üst köşe)
        tarih = datetime.now().strftime("%d/%m/%Y")
        tarih_genislik = c.stringWidth(tarih)
        c.drawRightString(550, 770, f"Tarih: {tarih}")

        # Sistem bilgilerini ekle
        c.setFont("Helvetica", 12)
        c.drawString(50, 700, "Marka:")
        c.drawString(150, 700, system_info['Model'])
        c.drawString(50, 680, "CPU:")
        c.drawString(150, 680, system_info['CPU'])
        c.drawString(50, 660, "Seri No:")
        c.drawString(150, 660, seri_no)
        c.drawString(50, 640, "Disk:")
        c.drawString(150, 640, system_info['Disk'])
        c.drawString(50, 620, "RAM:")
        c.drawString(150, 620, str(system_info['RAM']) + " GB")

        # Aksesuarlar bölümü ekle
        c.drawString(50, 600, "Teslim Edilen Aksesuarlar:")
        for i, aksesuar in enumerate(aksesuarlar):
            c.drawString(70, 580 - i*20, "- {}".format(aksesuar.strip()))

        # Teslim eden ve teslim alan bilgileri
        c.drawString(50, 470, "Teslim Eden:")
        c.drawString(150, 470, teslim_eden)
        c.drawString(50, 450, "Teslim Alan:")
        c.drawString(150, 450, teslim_alan)

        # Ek metin
        ek_metin = "Yukaridaki belirtilen özellikteki dizüstü bilgisayar ve aksesuarlar tarafimdan eksiksiz olarak teslim edilmistir."
        metin_genislik = c.stringWidth(ek_metin)
        c.drawString((600 - metin_genislik) / 2, 420, ek_metin)

        # İmza bölümü (biraz daha boşluk)
        c.drawString(50, 390, "Teslim Eden Imza:")

        # Boşluk bırak
        c.drawString(50, 350, "Teslim Alan Imza:")

        # PDF dosyasını kaydet
        c.save()
        print("Zimmet formu başarıyla oluşturuldu:")
        print("PDF Dosyasının Yolu:", pdf_yolu)
    except Exception as e:
        print("Hata:", e)

if __name__ == "__main__":
    system_info = get_system_info()

    if system_info is not None:
        print("System Information:")
        for key, value in system_info.items():
            print(f"{key}: {value}")
        
        create_inventory_form(system_info)
    else:
        print("Bilgiler alınamadı.")





